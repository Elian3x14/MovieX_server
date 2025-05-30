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

    def __str__(self):
        return self.email


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Movie(models.Model):
    NOW_SHOWING = "now-showing"
    COMING_SOON = "coming-soon"
    RELEASE_STATUS_CHOICES = [
        (NOW_SHOWING, "Now Showing"),
        (COMING_SOON, "Coming Soon"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    poster_url = models.URLField(blank=False)
    trailer_url = models.URLField(blank=True)
    backdrop_url = models.URLField(blank=True)
    genres = models.ManyToManyField(Genre, related_name="movies")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
    )
    duration = models.PositiveIntegerField()  # in minutes
    year = models.PositiveIntegerField()  # in YYYY format
    director = models.CharField(max_length=100)
    actors = models.ManyToManyField(Actor, related_name="movies")
    release_date = models.DateField()
    release_status = models.CharField(
        max_length=20,
        choices=RELEASE_STATUS_CHOICES,
        default=COMING_SOON,
    )

    def __str__(self):
        return self.title


class Cinema(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Room(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    total_seats = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.cinema.name}"

class SeatType(models.Model):
    name = models.CharField(max_length=50)  # VD: VIP, Standard, Couple
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.name

class Seat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    seat_row = models.CharField(max_length=1)
    seat_col = models.IntegerField()
    seat_type = models.ForeignKey(
        SeatType, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("room", "seat_row", "seat_col")

    def __str__(self):
        return f"{self.room.name} - Row: {self.seat_row}, Col: {self.seat_col}"

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.movie.title} - {self.room.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    expired_at = models.DateTimeField(null=True, blank=True)
    

    def __str__(self):
        return f"Booking {self.id} - {self.user.email} - {self.showtime.movie.title} - {self.booking_time.strftime('%Y-%m-%d %H:%M')}"

class BookingSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="booking_seats")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[
            ("reserved", "Reserved"),  # Ghế đã đặt
            ("hold", "Hold"),  # Ghế đang giữ bởi người dùng
            ("available", "Available"),  # Ghế còn trống
            ("unavailable", "Unavailable"),  # Ghế không khả dụng
        ],
        default="available",
    )
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    class Meta:
        unique_together = ("booking", "seat")

    def __str__(self):
        return f"BookingSeat {self.id} - Booking: {self.booking.id} - Seat: {self.seat.room.name} - Row: {self.seat.seat_row}, Col: {self.seat.seat_col}"

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    method = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - Booking: {self.booking.id} - Amount: {self.amount} - Method: {self.method}"


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews') 
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        default=0,
    )
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.author} - {self.rating}"
