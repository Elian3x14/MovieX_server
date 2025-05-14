from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _

# Regex cho số điện thoại Việt Nam: 10 số, bắt đầu bằng 03, 05, 07, 08, 09
vietnam_phone_regex = RegexValidator(
    regex=r"^(03|05|07|08|09)\d{8}$",
    message="Số điện thoại không hợp lệ. Vui lòng nhập số 10 chữ số bắt đầu bằng 03, 05, 07, 08, hoặc 09.",
)


class User(AbstractUser):
    ROLE_CHOICES = (("user", "User"), ("admin", "Admin"))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[vietnam_phone_regex],
        verbose_name=_("phone number"),
    )

    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    poster_url = models.URLField(blank=False)
    trailer_url = models.URLField(blank=True)
    backdrop_url = models.URLField(blank=True)
    genres = models.CharField(max_length=100)  # VD: Action, Comedy, Drama
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
    )
    duration = models.PositiveIntegerField()  # in minutes
    year = models.PositiveIntegerField()  # in YYYY format
    director = models.CharField(max_length=100)
    cast = models.TextField()  # VD: "Actor1, Actor2, Actor3"
    release_date = models.DateField()

    def __str__(self):
        return self.title


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
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)


class Seat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    seat_row = models.CharField(max_length=1)
    seat_col = models.IntegerField()
    seat_type = models.ForeignKey(
        SeatType, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("room", "seat_row", "seat_col")


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Booking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")


class BookingSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("booking", "seat")


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    method = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
