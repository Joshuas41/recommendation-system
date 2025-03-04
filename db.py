# import os
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv

# # Load biến môi trường từ file .env
# load_dotenv()

# # Lấy thông tin database từ .env
# DATABASE_URL = os.getenv("DATABASE_URL")

# # Tạo engine kết nối PostgreSQL
# engine = create_engine(DATABASE_URL)

# # Tạo session
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # # Kiểm tra kết nối
# # try:
# #     with engine.connect() as conn:
# #         print("✅ Kết nối PostgreSQL thành công!")
# # except Exception as e:
# #     print("❌ Lỗi kết nối:", e)
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import requests
import os
from dotenv import load_dotenv
from db import Movie, SessionLocal

# Load biến môi trường từ .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

app = FastAPI()

# Dependency lấy session từ database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Gọi API TMDB và lưu phim vào database
@app.get("/fetch_movies")
def fetch_movies(db: Session = Depends(get_db)):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for movie in data["results"]:
            db_movie = Movie(
                id=movie["id"],
                title=movie["title"],
                overview=movie["overview"],
                vote_average=movie["vote_average"],
                release_date=movie["release_date"]
            )
            db.add(db_movie)
        db.commit()
        return {"message": "✅ Dữ liệu phim đã được lưu!"}
    return {"error": "❌ Không thể lấy dữ liệu từ TMDB"}

# API để lấy danh sách phim từ database
@app.get("/movies")
def get_movies(db: Session = Depends(get_db)):
    movies = db.query(Movie).all()
    return {"movies": movies}
