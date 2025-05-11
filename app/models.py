from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (('user', 'User'), ('admin', 'Admin'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField()  # in minutes
    release_date = models.DateField()
    genre = models.CharField(max_length=100)
    poster_url = models.TextField(blank=True)
    trailer_url = models.TextField(blank=True)


class Cinema(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)


class Room(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    total_seats = models.PositiveIntegerField()


class SeatType(models.Model):
    name = models.CharField(max_length=50)  # VD: VIP, Standard, Couple
    extra_price = models.DecimalField(max_digits=6, decimal_places=2)  # Giá phụ thêm vào giá showtime


class Seat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    seat_row = models.CharField(max_length=1)
    seat_col = models.IntegerField()
    seat_type = models.ForeignKey(SeatType, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ('room', 'seat_row', 'seat_col')


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')


class BookingSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('booking', 'seat')


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    method = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
