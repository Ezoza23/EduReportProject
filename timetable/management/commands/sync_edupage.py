import requests
from datetime import date
from django.core.management.base import BaseCommand
from timetable.models import Teacher, Subject, Classroom, Group, TimetableCard, LessonRecord

HEADERS = {
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://ciu.edupage.org/timetable/",
    "User-Agent": "Mozilla/5.0"
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

def fetch_data():
    response = requests.post(
        "https://ciu.edupage.org/timetable/server/regulartt.js?__func=regularttGetData",
        json={"__args": [None, "13"], "__gsh": "00000000"},
        headers=HEADERS
    )
    return response.json()

def table_to_dict(table):
    columns = table.get("data_columns", [])
    rows = table.get("data_rows", [])
    if not rows:
        return []
    if isinstance(rows[0], dict):
        return rows
    return [dict(zip(columns, row)) for row in rows]

def decode_days(days_str):
    if not days_str:
        return []
    return [DAY_NAMES[i] for i, ch in enumerate(days_str) if ch == "1"]


class Command(BaseCommand):
    help = "Sync timetable data from EduPage"

    def handle(self, *args, **kwargs):
        today = date.today()

        self.stdout.write("Fetching from EduPage...")
        data = fetch_data()
        tables = data["r"]["dbiAccessorRes"]["tables"]

        db = {}
        for table in tables:
            db[table["id"]] = table_to_dict(table)

        # --- Sync Teachers ---
        self.stdout.write("Syncing teachers...")
        for t in db["teachers"]:
            Teacher.objects.update_or_create(
                edupage_id=t["id"],
                defaults={
                    "full_name": t.get("name", ""),
                    "short_name": t.get("short", ""),
                }
            )
        self.stdout.write(f"  ✅ {len(db['teachers'])} teachers")

        # --- Sync Subjects ---
        self.stdout.write("Syncing subjects...")
        for s in db["subjects"]:
            Subject.objects.update_or_create(
                edupage_id=s["id"],
                defaults={"name": s.get("name", "")}
            )
        self.stdout.write(f"  ✅ {len(db['subjects'])} subjects")

        # --- Sync Classrooms ---
        self.stdout.write("Syncing classrooms...")
        for c in db["classrooms"]:
            Classroom.objects.update_or_create(
                edupage_id=c["id"],
                defaults={"name": c.get("name", "")}
            )
        self.stdout.write(f"  ✅ {len(db['classrooms'])} classrooms")

        # --- Sync Groups ---
        self.stdout.write("Syncing groups...")
        for g in db["groups"]:
            Group.objects.update_or_create(
                edupage_id=g["id"],
                defaults={"name": g.get("name", "")}
            )
        self.stdout.write(f"  ✅ {len(db['groups'])} groups")

        # --- Sync Cards ---
        self.stdout.write("Syncing timetable cards...")

        lessons_map = {l["id"]: l for l in db["lessons"]}
        classes_map = {c["id"]: c for c in db["classes"]}

        # Get card IDs that have past lesson records — NEVER delete these
        protected_card_ids = set(
            LessonRecord.objects.filter(date__lt=today).values_list("card_id", flat=True)
        )
        self.stdout.write(f"  Protected cards (have past records): {len(protected_card_ids)}")

        # Delete only cards that are NOT protected
        TimetableCard.objects.exclude(id__in=protected_card_ids).delete()

        count = 0
        for card in db["cards"]:
            # Skip unscheduled cards
            if not card.get("period") or not card.get("days") or "1" not in card.get("days", ""):
                continue

            lesson = lessons_map.get(card.get("lessonid"), {})
            teacher_ids = lesson.get("teacherids", [])
            if not teacher_ids:
                continue

            teacher = Teacher.objects.filter(edupage_id=teacher_ids[0]).first()
            if not teacher:
                continue

            subject = Subject.objects.filter(
                edupage_id=lesson.get("subjectid", "")
            ).first()

            classroom_ids = card.get("classroomids", [])
            classroom = Classroom.objects.filter(
                edupage_id=classroom_ids[0]
            ).first() if classroom_ids else None

            days = decode_days(card.get("days", ""))
            period = card.get("period", "")

            class_ids = lesson.get("classids", [])
            class_names = ", ".join([
                classes_map.get(cid, {}).get("name", cid)
                for cid in class_ids
            ])

            group_ids = lesson.get("groupids", [])
            groups = Group.objects.filter(edupage_id__in=group_ids)

            for day in days:
                # If protected card exists for this teacher+day+period, update it
                protected = TimetableCard.objects.filter(
                    id__in=protected_card_ids,
                    teacher=teacher,
                    period=period,
                    day=day,
                ).first()

                if protected:
                    protected.subject = subject
                    protected.classroom = classroom
                    protected.class_names = class_names
                    protected.save()
                    protected.groups.set(groups)
                    count += 1
                else:
                    tc = TimetableCard.objects.create(
                        teacher=teacher,
                        subject=subject,
                        classroom=classroom,
                        day=day,
                        period=period,
                        class_names=class_names,
                    )
                    tc.groups.set(groups)
                    count += 1

        self.stdout.write(f"  ✅ {count} timetable cards")
        self.stdout.write(self.style.SUCCESS("All done!"))