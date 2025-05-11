from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import Cinema, Room, Seat, SeatType, Movie, Showtime
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed initial data'

    def handle(self, *args, **kwargs):
        # Tạo người dùng
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(username='admin', password='admin123', role='admin')
            self.stdout.write(self.style.SUCCESS('Admin user created'))

        if not User.objects.filter(username='user').exists():
            User.objects.create_user(username='user', password='user123', role='user')
            self.stdout.write(self.style.SUCCESS('Regular user created'))

        # Tạo các loại ghế
        vip = SeatType.objects.get_or_create(name='VIP', extra_price=50000)[0]
        standard = SeatType.objects.get_or_create(name='Standard', extra_price=0)[0]
        couple = SeatType.objects.get_or_create(name='Couple', extra_price=80000)[0]
        self.stdout.write(self.style.SUCCESS('Seat types created'))

        # Tạo rạp và phòng
        cinema = Cinema.objects.get_or_create(name='Galaxy Cinema', city='Ho Chi Minh', address='123 Nguyen Trai')[0]
        room = Room.objects.get_or_create(name='Room 1', cinema=cinema, total_seats=20)[0]

        # Tạo ghế trong phòng (5 hàng x 4 cột)
        Seat.objects.all().filter(room=room).delete()
        rows = ['A', 'B', 'C', 'D', 'E']
        for i, row in enumerate(rows):
            for col in range(1, 5):
                # A, B là VIP; C là Couple; còn lại Standard
                if row in ['A', 'B']:
                    seat_type = vip
                elif row == 'C':
                    seat_type = couple
                else:
                    seat_type = standard
                Seat.objects.get_or_create(room=room, seat_row=row, seat_col=col, seat_type=seat_type)
        self.stdout.write(self.style.SUCCESS('Seats created'))

        # Tạo phim
        movie = Movie.objects.get_or_create(
            title='Inception',
            description='Mind-bending sci-fi thriller.',
            duration=148,
            release_date='2010-07-16',
            genre='Sci-Fi',
            poster_url='https://example.com/inception.jpg',
            trailer_url='https://youtube.com/watch?v=YoHD9XEInc0',
        )[0]
        self.stdout.write(self.style.SUCCESS('Movie created'))

        # Tạo suất chiếu
        now = timezone.now()
        showtime = Showtime.objects.get_or_create(
            movie=movie,
            room=room,
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, minutes=148),
            price=90000  # Giá cơ bản, chưa gồm phụ thu loại ghế
        )[0]
        self.stdout.write(self.style.SUCCESS('Showtime created'))

        self.stdout.write(self.style.SUCCESS('Seeding completed successfully.'))
