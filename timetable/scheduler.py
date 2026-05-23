from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.core.management import call_command


def sync_job():
    print("Running scheduled EduPage sync...")
    call_command("sync_edupage")
    print("Sync complete!")


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        sync_job,
        trigger="interval",
        hours=24,
        id="sync_edupage",
        replace_existing=True,
    )

    scheduler.start()
    print("Scheduler started — syncing every 24 hours")