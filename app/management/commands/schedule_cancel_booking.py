from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from json import dumps

class Command(BaseCommand):
    help = "Schedule task to cancel expired bookings"

    def handle(self, *args, **kwargs):
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )
        PeriodicTask.objects.update_or_create(
            name='Cancel expired bookings',
            defaults={
                'interval': schedule,
                'task': 'app.tasks.cancel_expired_bookings',
                'args': dumps([]),
            }
        )
        self.stdout.write("Scheduled cancel_expired_bookings task.")
