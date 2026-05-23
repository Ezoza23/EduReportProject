from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    edupage_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50, blank=True)
    is_dean = models.BooleanField(default=False)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='teachers')
    def __str__(self):
        return self.full_name


class Subject(models.Model):
    edupage_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Classroom(models.Model):
    edupage_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Group(models.Model):
    edupage_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class TimetableCard(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="cards")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True)
    groups = models.ManyToManyField(Group, blank=True)
    class_names = models.CharField(max_length=500, blank=True)  # 👈 add this
    day = models.CharField(max_length=20)
    period = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.teacher} | {self.subject} | {self.day} P{self.period}"

class LessonRecord(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="lesson_records")
    card = models.ForeignKey(TimetableCard, on_delete=models.CASCADE)
    date = models.DateField()
    is_covered = models.BooleanField(null=True, default=None)  # None=not marked, True=covered, False=not covered
    is_replaced = models.BooleanField(default=False)
    replacement_date = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ("card", "date")

    def __str__(self):
        return f"{self.teacher} | {self.date} | {'✓' if self.is_covered else '✗'}"

class MonthlyReport(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
    ]
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="reports")
    year = models.IntegerField()
    month = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("teacher", "year", "month")

    def __str__(self):
        return f"{self.teacher} | {self.year}-{self.month} | {self.status}"
class ReportDeadline(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    deadline = models.DateField()
    set_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ("year", "month")

    def __str__(self):
        return f"{self.year}-{self.month} deadline: {self.deadline}"
class Department(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name