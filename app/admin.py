from django.contrib import admin
from django.utils.html import format_html
from .models import *

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'showtime', 'colored_status', 'expired_at', 'total_amount')
    list_filter = ('status', 'showtime')
    search_fields = ('user__username', 'showtime__movie__title')
    readonly_fields = ('expired_at',)
    
    def colored_status(self, obj):
        color = {
            'pending': 'orange',
            'confirmed': 'green',
            'cancelled': 'red',
            'expired': 'gray',
        }.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.status.capitalize()
        )
    colored_status.short_description = 'Status'
    colored_status.admin_order_field = 'status'


# Register your models here.
admin.site.register(User)
admin.site.register(Actor)
admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Cinema)
admin.site.register(Room)
admin.site.register(SeatType)
admin.site.register(Seat)
admin.site.register(Showtime)
admin.site.register(Booking, BookingAdmin)
admin.site.register(BookingSeat)
admin.site.register(Payment)
