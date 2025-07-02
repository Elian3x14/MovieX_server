from django.core.management.base import BaseCommand
from app.models import Actor

class Command(BaseCommand):
    help = "Seed actors"

    def handle(self, *args, **kwargs):
        actor_names = [
            "Leonardo DiCaprio", "Tom Hanks", "Natalie Portman",
            "Robert Downey Jr.", "Scarlett Johansson", "Denzel Washington",
            "Jennifer Lawrence", "Brad Pitt", "Morgan Freeman", "Emma Stone",
        ]
        created = 0
        for name in actor_names:
            _, is_created = Actor.objects.get_or_create(name=name)
            if is_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Đã seed {created} diễn viên."))
