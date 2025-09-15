from django.core.management.base import BaseCommand
from app.models import Room, Cinema

class Command(BaseCommand):
    help = "Seed phòng chiếu cho các rạp có sẵn"

    def handle(self, *args, **kwargs):
        cinemas = Cinema.objects.all()
        created = 0

        for cinema in cinemas:
            for i in range(1, 4):  # Mỗi rạp tạo 3 phòng
                room_name = f"Phòng {i}"
                room, is_created = Room.objects.get_or_create(
                    cinema=cinema,
                    name=room_name,
                    defaults={
                        "no_row": 5,       # Ví dụ 5 hàng
                        "no_column": 8     # Ví dụ 8 cột
                    }
                )
                if is_created:
                    room.create_seats()  # Gọi hàm tự tạo ghế
                    created += 1

        self.stdout.write(self.style.SUCCESS(f"Đã tạo {created} phòng chiếu."))
