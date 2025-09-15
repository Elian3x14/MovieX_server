from django.core.management.base import BaseCommand
from app.models import SeatType

class Command(BaseCommand):
    help = "Seed loại ghế (SeatType)"

    def handle(self, *args, **kwargs):
        seat_types = [
            {"name": "Ghế VIP", "short_name": "VIP", "color": "#FFD700"},
            {"name": "Ghế thường", "short_name": "STD", "color": "#C0C0C0"},
            {"name": "Ghế đôi", "short_name": "COUPLE", "color": "#FF69B4"},
            {"name": "Ghế trẻ em", "short_name": "KID", "color": "#ADD8E6"},
        ]
        created = 0
        for seat in seat_types:
            _, is_created = SeatType.objects.get_or_create(
                name=seat["name"],
                defaults={"short_name": seat["short_name"], "color": seat["color"]},
            )
            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Đã seed {created} loại ghế."))
