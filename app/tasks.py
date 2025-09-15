# tasks.py
from celery import shared_task
from django.utils import timezone
import logging
from .models import Booking

logger = logging.getLogger(__name__)

@shared_task
def cancel_expired_bookings():
    now = timezone.now()
    expired_bookings = Booking.objects.filter(status="pending", expired_at__lte=now)
    logger.info(f"Found {expired_bookings.count()} expired bookings to cancel")
    
    for booking in expired_bookings:
        booking.status = "expired"
        booking.save()
        # Optional: release seats logic here
