from django.core.management.base import BaseCommand
from app.management.commands.seeds import (
    seed_users,
    seed_seat_types,
    seed_cinema_and_room,
    seed_seats,
    seed_movies,
    seed_actors,
    seed_showtimes,
    seed_genres,
)


class Command(BaseCommand):
    help = "Seed initial data"

    def handle(self, *args, **kwargs):
        seed_users()
        self.stdout.write(self.style.SUCCESS("Users seeded"))

        vip, standard, couple = seed_seat_types()
        self.stdout.write(self.style.SUCCESS("Seat types seeded"))

        cinema, room = seed_cinema_and_room()
        self.stdout.write(self.style.SUCCESS("Cinema and room seeded"))

        seed_seats(room, vip, standard, couple)
        self.stdout.write(self.style.SUCCESS("Seats seeded"))

        seed_actors()
        self.stdout.write(self.style.SUCCESS("Actors seeded"))

        seed_genres()
        self.stdout.write(self.style.SUCCESS("Genres seeded"))

        movies = seed_movies()
        self.stdout.write(self.style.SUCCESS("Movie seeded"))

        seed_showtimes()
        self.stdout.write(self.style.SUCCESS("Showtime seeded"))

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully."))
