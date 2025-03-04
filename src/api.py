from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Initialize FastAPI app
app = FastAPI()

@app.get("/movies/")
def get_movies(
    year: int = Query(None, description="Filter by release year"),
    min_rating: float = Query(None, description="Minimum vote average")
):
    """Get movies with optional filters"""
    query = "SELECT id, title, release_date, vote_average, overview, poster_path FROM movies"
    conditions = []
    
    if year:
        conditions.append(f"EXTRACT(YEAR FROM release_date) = {year}")
    if min_rating:
        conditions.append(f"vote_average >= {min_rating}")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    with engine.connect() as conn:
        result = conn.execute(text(query))
        movies = [dict(row) for row in result.mappings()]
    
    return {"movies": movies}

@app.get("/movies/search/")
def search_movies(title: str):
    """Search movies by title"""
    query = text("SELECT * FROM movies WHERE title ILIKE :title")
    with engine.connect() as conn:
        result = conn.execute(query, {"title": f"%{title}%"})
        movies = [dict(row) for row in result.mappings()]
    return {"movies": movies}

@app.get("/movies/{movie_id}")
def get_movie_details(movie_id: int):
    """Get movie details by ID"""
    query = text("SELECT * FROM movies WHERE id = :movie_id")
    with engine.connect() as conn:
        result = conn.execute(query, {"movie_id": movie_id}).mappings().first()
    if result:
        return result
    return {"error": "Movie not found"}
