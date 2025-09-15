from django.core.management.base import BaseCommand
from app.models import Movie, Genre, Actor
from django.utils.text import slugify
from datetime import date, timedelta
import random


movies_data = [
    {
        "title": "Inception",
        "description": "A mind-bending thriller about dreams within dreams.",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BMjExMjkwNTQ0Nl5BMl5BanBnXkFtZTcwNTY0OTk1Mw@@._V1_.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=JEv8W3pWqH0",
        "backdrop_url": "https://images2.alphacoders.com/851/85182.jpg",
        "rating": 8.8,
        "duration": 148,
        "year": 2010,
        "director": "Christopher Nolan",
        "release_date": date.today() - timedelta(days=365 * 14),
    },
    {
        "title": "Interstellar",
        "description": "Explorers travel through a wormhole in space.",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BYzdjMDAxZGItMjI2My00ODA1LTlkNzItOWFjMDU5ZDJlYWY3XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
        "backdrop_url": "https://images8.alphacoders.com/560/560736.jpg",
        "rating": 8.6,
        "duration": 169,
        "year": 2014,
        "director": "Christopher Nolan",
        "release_date": date.today() - timedelta(days=365 * 10),
    },
    {
        "title": "The Matrix",
        "description": "A hacker discovers the world is a simulation.",
        "poster_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfSjSWOCaw5dnDL2GT1zFd9RMCgUGw5Q2Cfg&s",
        "trailer_url": "https://youtube.com/watch?v=vKQi3bBA1y8",
        "backdrop_url": "https://www.wallpaperflare.com/static/794/952/936/the-matrix-matrix-movie-wallpaper.jpg",
        "rating": 8.7,
        "duration": 136,
        "year": 1999,
        "director": "Lana Wachowski",
        "release_date": date.today() - timedelta(days=365 * 25),
    },
    {
        "title": "Avengers: Endgame",
        "description": "The Avengers assemble for a final battle.",
        "poster_url": "https://m.media-amazon.com/images/I/81pTbZF5KXL._AC_SL1500_.jpg",
        "trailer_url": "https://youtube.com/watch?v=TcMBFSGVi1c",
        "backdrop_url": "https://wallpapers.com/images/hd/avengers-endgame-superheroes-2ujw4a3pp2gh8xpf.jpg",
        "rating": 8.4,
        "duration": 181,
        "year": 2019,
        "director": "Anthony Russo",
        "release_date": date.today() - timedelta(days=365 * 5),
    },
    {
        "title": "Oppenheimer",
        "description": "The story of the atomic bomb creator.",
        "poster_url": "https://example.com/posters/oppenheimer.jpg",
        "trailer_url": "https://youtube.com/watch?v=uYPbbksJxIg",
        "backdrop_url": "https://example.com/backdrops/oppenheimer.jpg",
        "rating": 8.6,
        "duration": 180,
        "year": 2023,
        "director": "Christopher Nolan",
        "release_date": date.today() - timedelta(days=300),
    },
    {
        "title": "Dune: Part Two",
        "description": "Paul Atreides unites the Fremen to wage war.",
        "poster_url": "https://example.com/posters/dune2.jpg",
        "trailer_url": "https://youtube.com/watch?v=Way9Dexny3w",
        "backdrop_url": "https://example.com/backdrops/dune2.jpg",
        "rating": 8.3,
        "duration": 166,
        "year": 2024,
        "director": "Denis Villeneuve",
        "release_date": date.today() + timedelta(days=30),
    },
    {
        "title": "The Batman",
        "description": "Batman faces the Riddler in Gotham.",
        "poster_url": "https://example.com/posters/batman.jpg",
        "trailer_url": "https://youtube.com/watch?v=mqqft2x_Aa4",
        "backdrop_url": "https://example.com/backdrops/batman.jpg",
        "rating": 7.9,
        "duration": 176,
        "year": 2022,
        "director": "Matt Reeves",
        "release_date": date.today() - timedelta(days=365 * 2),
    },
    {
        "title": "Django Unchained",
        "description": "A freed slave sets out to rescue his wife.",
        "poster_url": "https://example.com/posters/django.jpg",
        "trailer_url": "https://youtube.com/watch?v=eUdM9vrCbow",
        "backdrop_url": "https://example.com/backdrops/django.jpg",
        "rating": 8.4,
        "duration": 165,
        "year": 2012,
        "director": "Quentin Tarantino",
        "release_date": date.today() - timedelta(days=365 * 12),
    },
    {
        "title": "La La Land",
        "description": "A jazz musician and an actress fall in love.",
        "poster_url": "https://example.com/posters/lalaland.jpg",
        "trailer_url": "https://youtube.com/watch?v=0pdqf4P9MB8",
        "backdrop_url": "https://example.com/backdrops/lalaland.jpg",
        "rating": 8.0,
        "duration": 128,
        "year": 2016,
        "director": "Damien Chazelle",
        "release_date": date.today() - timedelta(days=365 * 8),
    },
    {
        "title": "The Marvels",
        "description": "Carol Danvers joins forces with Ms. Marvel.",
        "poster_url": "https://example.com/posters/marvels.jpg",
        "trailer_url": "https://youtube.com/watch?v=iuk77TjvfmE",
        "backdrop_url": "https://example.com/backdrops/marvels.jpg",
        "rating": 6.3,
        "duration": 105,
        "year": 2023,
        "director": "Nia DaCosta",
        "release_date": date.today() + timedelta(days=20),
    },
]


class Command(BaseCommand):
    help = "Seed dữ liệu cho phim (Movie)"

    def handle(self, *args, **kwargs):
        genres = list(Genre.objects.all())
        actors = list(Actor.objects.all())

        if not genres or not actors:
            self.stdout.write(self.style.ERROR("Hãy seed Genre và Actor trước."))
            return

        created = 0
        for data in movies_data:
            movie, is_created = Movie.objects.get_or_create(
                title=data["title"],
                defaults={key: val for key, val in data.items() if key != "title"},
            )

            if is_created:
                # Random 1-3 thể loại
                movie.genres.set(random.sample(genres, k=min(3, len(genres))))
                # Random 2-5 diễn viên
                movie.actors.set(random.sample(actors, k=min(5, len(actors))))
                movie.save()
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Đã seed {created} phim thành công."))
