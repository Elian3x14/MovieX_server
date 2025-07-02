from django.core.management.base import BaseCommand
from app.models import SeatType

class Command(BaseCommand):
    help = "Seed loại ghế (SeatType)"

    def handle(self, *args, **kwargs):
        seat_types = [
            {"name": "Ghế VIP", "short_name": "VIP"},
            {"name": "Ghế thường", "short_name": "STD"},
            {"name": "Ghế đôi", "short_name": "COUPLE"},
            {"name": "Ghế trẻ em", "short_name": "KID"},
        ]
        created = 0
        for seat in seat_types:
            _, is_created = SeatType.objects.get_or_create(
                name=seat["name"],
                defaults={"short_name": seat["short_name"]}
            )
            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Đã seed {created} loại ghế."))
