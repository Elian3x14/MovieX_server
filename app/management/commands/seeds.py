from django.utils import timezone
from datetime import timedelta
from app.models import *
from django.contrib.auth import get_user_model
import random
from datetime import date, timedelta

User = get_user_model()


def seed_genres():
    genre_names = [
        "Action",
        "Adventure",
        "Comedy",
        "Drama",
        "Fantasy",
        "Horror",
        "Romance",
        "Science Fiction",
        "Thriller",
        "Animation",
    ]

    for name in genre_names:
        Genre.objects.get_or_create(name=name)


def seed_actors():
    actor_names = [
        "Leonardo DiCaprio",
        "Tom Hanks",
        "Natalie Portman",
        "Robert Downey Jr.",
        "Scarlett Johansson",
        "Denzel Washington",
        "Jennifer Lawrence",
        "Brad Pitt",
        "Morgan Freeman",
        "Emma Stone",
    ]

    for name in actor_names:
        Actor.objects.get_or_create(name=name)


def seed_users():
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Xóa tất cả người dùng trước khi tạo mới
    User.objects.all().delete()
    if not User.objects.filter(email="admin@example.com").exists():
        User.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="admin123",
            role="admin",
            phone_number="0900000001",
            first_name="Admin",
            last_name="User",
        )

    if not User.objects.filter(email="user@example.com").exists():
        User.objects.create_user(
            email="user@example.com",
            username="user",
            password="user123",
            role="user",
            phone_number="0900000002",
            first_name="Normal",
            last_name="User",
        )


def seed_seat_types():
    vip = SeatType.objects.get_or_create(name="VIP", extra_price=50000)[0]
    standard = SeatType.objects.get_or_create(name="Standard", extra_price=0)[0]
    couple = SeatType.objects.get_or_create(name="Couple", extra_price=80000)[0]
    return vip, standard, couple


def seed_cinema_and_room():
    cinema = Cinema.objects.get_or_create(
        name="Galaxy Cinema", city="Ho Chi Minh", address="123 Nguyen Trai"
    )[0]
    room = Room.objects.get_or_create(name="Room 1", cinema=cinema, total_seats=20)[0]
    return cinema, room


def seed_seats(room, vip, standard, couple):
    Seat.objects.filter(room=room).delete()
    rows = ["A", "B", "C", "D", "E"]
    for row in rows:
        for col in range(1, 5):
            if row in ["A", "B"]:
                seat_type = vip
            elif row == "C":
                seat_type = couple
            else:
                seat_type = standard
            Seat.objects.get_or_create(
                room=room, seat_row=row, seat_col=col, seat_type=seat_type
            )


def seed_movies():

    genres = list(Genre.objects.all())
    actors = list(Actor.objects.all())

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
            "release_status": Movie.NOW_SHOWING,
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
            "release_status": Movie.NOW_SHOWING,
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
            "release_status": Movie.NOW_SHOWING,
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
            "release_status": Movie.NOW_SHOWING,
        },
        # Thêm các bộ phim khác ở đây
    ]

    for data in movies_data:
        movie, _ = Movie.objects.get_or_create(
            title=data["title"],
            defaults={key: val for key, val in data.items() if key != "title"},
        )
        # Thêm 1-3 genres ngẫu nhiên
        selected_genres = random.sample(genres, k=min(3, len(genres)))
        movie.genres.set(selected_genres)

        # Thêm 2-5 actors ngẫu nhiên
        selected_actors = random.sample(actors, k=min(5, len(actors)))
        movie.actors.set(selected_actors)

        movie.save()


def seed_showtimes():
    rooms = Room.objects.all()
    movies = Movie.objects.all()
    cinemas = Cinema.objects.all()

    for movie in movies:
        for room in rooms:
            # Tạo 5-10 showtime cho mỗi bộ phim
            for _ in range(random.randint(5, 10)):
                start_time = timezone.now() + timedelta(days=random.randint(0, 30))
                end_time = start_time + timedelta(hours=random.randint(1, 3))
                showtime = Showtime.objects.create(
                    movie=movie,
                    room=room,
                    start_time=start_time,
                    price=random.randint(50000, 200000),
                    end_time=end_time,
                )
                showtime.save()


"""

        
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
            "release_status": Movie.NOW_SHOWING,
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
            "release_status": Movie.COMING_SOON,
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
            "release_status": Movie.NOW_SHOWING,
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
            "release_status": Movie.NOW_SHOWING,
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
            "release_status": Movie.NOW_SHOWING,
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
            "release_status": Movie.COMING_SOON,
        },
    """
