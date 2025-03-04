import os
import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# API Key & Database URL
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Tạo kết nối PostgreSQL
engine = create_engine(DATABASE_URL)

def fetch_movies_by_year(year):
    """ Gọi API TMDB để lấy danh sách phim theo năm """
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=en-US&primary_release_year={year}&page=1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"❌ Lỗi khi lấy dữ liệu năm {year}: {response.status_code}")
        return []

def save_genres_to_db(genres):
    """ Lưu danh sách thể loại vào bảng genres """
    with engine.connect() as conn:
        for genre in genres:
            query = text("""
                INSERT INTO genres (id, name)
                VALUES (:id, :name)
                ON CONFLICT (id) DO NOTHING
            """)
            conn.execute(query, {"id": genre["id"], "name": genre["name"]})
        conn.commit()
    print("✅ Đã lưu danh sách thể loại!")

def save_movies_to_db(movies):
    """ Lưu danh sách phim và liên kết với thể loại vào PostgreSQL """
    with engine.connect() as conn:
        for movie in movies:
            # Lưu phim vào bảng movies
            query_movie = text("""
                INSERT INTO movies (id, title, overview, release_date, vote_average, poster_path)
                VALUES (:id, :title, :overview, :release_date, :vote_average, :poster_path)
                ON CONFLICT (id) DO NOTHING
            """)
            conn.execute(query_movie, {
                "id": movie["id"],
                "title": movie["title"],
                "overview": movie["overview"],
                "release_date": movie["release_date"],
                "vote_average": movie["vote_average"],
                "poster_path": movie["poster_path"]
            })

            # Lưu mối quan hệ phim - thể loại vào bảng movie_genres
            for genre_id in movie["genre_ids"]:
                query_movie_genre = text("""
                    INSERT INTO movie_genres (movie_id, genre_id)
                    VALUES (:movie_id, :genre_id)
                    ON CONFLICT DO NOTHING
                """)
                conn.execute(query_movie_genre, {"movie_id": movie["id"], "genre_id": genre_id})

        conn.commit()
    print("✅ Dữ liệu phim và thể loại đã được lưu vào PostgreSQL!")

if __name__ == "__main__":
    # Lấy danh sách thể loại từ TMDB
    print("📦 Đang lấy danh sách thể loại...")
    genres_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    genres_response = requests.get(genres_url)
    if genres_response.status_code == 200:
        genres = genres_response.json().get("genres", [])
        save_genres_to_db(genres)
    else:
        print("❌ Lỗi khi lấy danh sách thể loại!")

    # Lấy danh sách phim theo năm và lưu vào database
    years = range(2010, 2025)
    for year in years:
        print(f"📅 Đang lấy phim của năm {year}...")
        movies = fetch_movies_by_year(year)
        if movies:
            save_movies_to_db(movies)
