from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from app.models import Movie, Room, Showtime

class Command(BaseCommand):
    help = "Seed dữ liệu cho suất chiếu phim (Showtime)"

    def handle(self, *args, **kwargs):
        movies = Movie.objects.all()
        rooms = Room.objects.all()

        if not movies.exists() or not rooms.exists():
            self.stdout.write(self.style.ERROR("Cần seed Movie và Room trước khi tạo Showtime."))
            return

        count = 0

        for movie in movies:
            for room in rooms:
                for _ in range(random.randint(3, 6)):  # mỗi phim có 3-6 suất chiếu mỗi phòng
                    # thời gian bắt đầu ngẫu nhiên trong vòng 30 ngày tới
                    start_time = timezone.now() + timedelta(
                        days=random.randint(0, 30),
                        hours=random.choice([9, 12, 15, 18, 21])  # khung giờ cố định
                    )
                    end_time = start_time + timedelta(minutes=movie.duration + 20)  # cộng thêm 20 phút vệ sinh

                    Showtime.objects.create(
                        movie=movie,
                        room=room,
                        start_time=start_time,
                        end_time=end_time
                    )
                    count += 1

        self.stdout.write(self.style.SUCCESS(f"Đã tạo {count} suất chiếu phim (Showtime)."))
