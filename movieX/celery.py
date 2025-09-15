from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movieX.settings")

app = Celery("movieX")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'cancel-expired-bookings-every-minute': {
        'task': 'app.tasks.cancel_expired_bookings',
        'schedule': 60.0,  # chạy mỗi 60 giây
    },
}
