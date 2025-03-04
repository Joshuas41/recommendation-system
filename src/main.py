from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Khởi tạo FastAPI
app = FastAPI()

# Kết nối PostgreSQL
DATABASE_URL = "postgresql://postgres:Anhkha1@localhost:5432/recommendation_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Route để lấy danh sách phim
@app.get("/movies")
def get_movies():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM movies"))
        movies = [dict(row) for row in result.mappings()]
    return {"movies": movies}

# Chạy server bằng lệnh: uvicorn main:app --reload
