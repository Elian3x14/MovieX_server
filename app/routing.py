from django.urls import re_path
from .consumers import BookingConsumer

websocket_urlpatterns = [
    re_path(r'ws/booking/(?P<booking_id>\d+)/$', BookingConsumer.as_asgi()),
]
