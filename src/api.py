from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

app = FastAPI()

@app.get("/movies/")
def get_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str = Query(None, min_length=1, max_length=100)
):
    """API lấy danh sách phim có phân trang và hỗ trợ tìm kiếm theo tên"""
    offset = (page - 1) * page_size

    query = """
        SELECT id, title, release_date, vote_average, overview, poster_path
        FROM movies
    """
    
    params = {"page_size": page_size, "offset": offset}

    # Nếu có tìm kiếm, thêm điều kiện vào câu query
    if search:
        query += " WHERE LOWER(title) LIKE LOWER(:search)"
        params["search"] = f"%{search}%"

    query += " ORDER BY release_date DESC LIMIT :page_size OFFSET :offset"

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        movies = [dict(row._mapping) for row in result]  

    return {"page": page, "page_size": page_size, "movies": movies}
