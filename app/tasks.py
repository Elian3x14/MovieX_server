# tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Booking

@shared_task
def cancel_expired_bookings():
    now = timezone.now()
    expired_bookings = Booking.objects.filter(status="pending", expired_at__lte=now)

    for booking in expired_bookings:
        booking.status = "cancelled"
        booking.save()
        # Optional: release seats logic here
