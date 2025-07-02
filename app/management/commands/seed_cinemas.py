from django.core.management.base import BaseCommand
from app.models import Cinema

class Command(BaseCommand):
    help = "Seed danh sách rạp chiếu phim"

    def handle(self, *args, **kwargs):
        cinema_data = [
            {
                "name": "CGV Nguyễn Chí Thanh",
                "street": "116 Nguyễn Chí Thanh",
                "ward": "Láng Thượng",
                "district": "Đống Đa",
                "city": "Hà Nội",
            },
            {
                "name": "Galaxy Nguyễn Du",
                "street": "116 Nguyễn Du",
                "ward": "Bến Thành",
                "district": "Quận 1",
                "city": "TP.HCM",
            },
            {
                "name": "Lotte Cinema Gò Vấp",
                "street": "242 Nguyễn Văn Lượng",
                "ward": "10",
                "district": "Gò Vấp",
                "city": "TP.HCM",
            },
        ]

        created = 0
        for data in cinema_data:
            _, is_created = Cinema.objects.get_or_create(name=data["name"], defaults=data)
            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Đã seed {created} rạp chiếu phim."))
