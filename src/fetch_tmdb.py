import os
import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Lấy thông tin API Key và Database URL từ file .env
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Tạo kết nối PostgreSQL
engine = create_engine(DATABASE_URL)

# API TMDB: Lấy danh sách phim phổ biến
TMDB_URL = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"

def fetch_movies():
    """ Gọi API TMDB để lấy danh sách phim """
    response = requests.get(TMDB_URL)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print("❌ Lỗi khi lấy dữ liệu từ TMDB:", response.status_code)
        return []

def save_movies_to_db(movies):
    """ Lưu danh sách phim vào PostgreSQL """
    with engine.connect() as conn:
        for movie in movies:
            query = text("""
                INSERT INTO movies (title, overview, release_date, vote_average, poster_path)
                VALUES (:title, :overview, :release_date, :vote_average, :poster_path)
            """)
            conn.execute(query, {
                "title": movie["title"],
                "overview": movie["overview"],
                "release_date": movie["release_date"],
                "vote_average": movie["vote_average"],
                "poster_path": movie["poster_path"]
            })
        conn.commit()
    print("✅ Dữ liệu đã được lưu vào PostgreSQL!")

# Chạy chương trình
if __name__ == "__main__":
    movies = fetch_movies()
    if movies:
        save_movies_to_db(movies)
