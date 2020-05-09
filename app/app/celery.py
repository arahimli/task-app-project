# import os
#
# from celery import Celery
#
# # Set default Django settings
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
#
# app = Celery('mysite')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()


from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery import shared_task
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))



@shared_task
def remove_expiry_file():
    import datetime
    from content.models import SharedFile
    SharedFile.objects.filter(expiration_date__lte=datetime.datetime.now())
    return "Task finished"



app.conf.beat_schedule = {
    "beat-celery-remove-expiry-file": {
        "task": "app.celery.remove_expiry_file",
        "schedule": crontab(minute='*/10'),  # 600 = every 10 minutes
        "args": [],
    },
}
