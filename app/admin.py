from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Movie)
admin.site.register(Cinema)
admin.site.register(Room)
admin.site.register(SeatType)
admin.site.register(Seat)
admin.site.register(Showtime)
admin.site.register(Booking)
admin.site.register(BookingSeat)
admin.site.register(Payment)
admin.site.register(User)

