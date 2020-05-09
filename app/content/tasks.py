# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.schedules import crontab

@shared_task
def remove_expiry_file():
    import datetime
    from content.models import SharedFile
    SharedFile.objects.filter(expiration_date__lte=datetime.datetime.now())
    return "Task finished"



app.conf.beat_schedule = {
    # "see-you-in-ten-seconds-task": {
    #     "task": "elombard.celery.see_youso",
    #     "schedule": 10.0,
    #     "args": [],
    # },
    "daily-progress-bar-month-calculate": {
        "task": "elombard.celery.progress_bar_calculate_month_difference",
        # "schedule": 250.0,
        # "schedule": 3.0,
        # 'schedule': datetime.timedelta(seconds=900), # 300 = every 5 minutes
        "schedule": crontab(minute='*/15'),
        # "schedule": crontab(hour=0, minute=35),
        # "schedule": crontab(hour=0, minute=20),
        "args": [],
    },
}