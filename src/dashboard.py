import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Set page config
st.set_page_config(page_title="Movie Dashboard", layout="wide")

# Load data
def get_movies():
    query = "SELECT id, title, release_date, vote_average, overview, poster_path FROM movies"
    return pd.read_sql(query, engine)

movies_df = get_movies()
movies_df["release_date"] = pd.to_datetime(movies_df["release_date"])
movies_df["year"] = movies_df["release_date"].dt.year

# Sidebar filters
st.sidebar.header("Filters")
min_year, max_year = movies_df["year"].min(), movies_df["year"].max()
selected_years = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))
min_rating, max_rating = movies_df["vote_average"].min(), movies_df["vote_average"].max()
selected_rating = st.sidebar.slider("Select Rating Range", min_rating, max_rating, (min_rating, max_rating))

# Apply filters
filtered_df = movies_df[(movies_df["year"] >= selected_years[0]) & (movies_df["year"] <= selected_years[1]) & (movies_df["vote_average"] >= selected_rating[0]) & (movies_df["vote_average"] <= selected_rating[1])]

# Dashboard title
st.title("\U0001F3A5 Movie Dashboard")
st.markdown("Danh sách phim được lấy từ PostgreSQL")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Number of Movies per Year")
    fig, ax = plt.subplots()
    filtered_df["year"].value_counts().sort_index().plot(kind="bar", ax=ax, color="skyblue")
    st.pyplot(fig)

with col2:
    st.subheader("Average Rating per Year")
    fig, ax = plt.subplots()
    filtered_df.groupby("year")["vote_average"].mean().plot(kind="line", ax=ax, marker="o", color="orange")
    st.pyplot(fig)

# Movie list with posters
st.subheader("Movie List")
for index, row in filtered_df.iterrows():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(f"https://image.tmdb.org/t/p/w200{row['poster_path']}", width=100)
    with col2:
        st.write(f"### {row['title']} ({row['year']})")
        st.write(f"⭐ {row['vote_average']}")
        st.write(row['overview'])
    st.markdown("---")
