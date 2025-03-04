import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = "http://127.0.0.1:8000/movies"

# Set page config
st.set_page_config(page_title="Movie Dashboard", layout="wide")

@st.cache_data
def get_movies(search="", page=1, page_size=100):
    """Fetch dữ liệu phim từ API với hỗ trợ tìm kiếm"""
    params = {"page": page, "page_size": page_size}
    if search:
        params["search"] = search

    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        movies = response.json()["movies"]
        df = pd.DataFrame(movies)
        df["release_date"] = pd.to_datetime(df["release_date"])
        df["year"] = df["release_date"].dt.year
        return df
    else:
        st.error("❌ Không thể tải dữ liệu từ API")
        return pd.DataFrame()

# 🎛️ **Sidebar - Bộ lọc phim**
st.sidebar.header("🎛️ Bộ lọc phim")

# 🔍 **Tìm kiếm phim**
search_query = st.sidebar.text_input("🔍 Tìm kiếm phim", "")

# 📥 **Fetch data từ API**
movies_df = get_movies(search=search_query)

# ⚠️ **Nếu không có phim nào, hiển thị thông báo**
if movies_df.empty:
    st.warning("⚠️ Không tìm thấy phim nào!")
    st.stop()

# 📅 **Lọc theo năm**
min_year = int(movies_df["year"].min())
max_year = int(movies_df["year"].max())
selected_years = st.sidebar.slider("📅 Chọn khoảng năm", min_year, max_year, (min_year, max_year))

# ⭐ **Lọc theo điểm đánh giá**
min_rating, max_rating = movies_df["vote_average"].min(), movies_df["vote_average"].max()
selected_rating = st.sidebar.slider("⭐ Điểm đánh giá", min_rating, max_rating, (min_rating, max_rating))

# 🔎 **Áp dụng bộ lọc**
filtered_df = movies_df[
    (movies_df["year"] >= selected_years[0]) &
    (movies_df["year"] <= selected_years[1]) &
    (movies_df["vote_average"] >= selected_rating[0]) &
    (movies_df["vote_average"] <= selected_rating[1])
]

# 🎬 **Dashboard title**
st.title("🎬 Movie Dashboard")
st.markdown("🚀 Danh sách phim lấy từ PostgreSQL")

# --- **BIỂU ĐỒ** ---
col1, col2 = st.columns(2)

# 📊 **Biểu đồ số lượng phim theo năm**
with col1:
    st.subheader("📊 Số lượng phim mỗi năm")
    fig, ax = plt.subplots(figsize=(8, 4))
    filtered_df["year"].value_counts().sort_index().plot(kind="bar", ax=ax, color="skyblue")
    ax.set_ylabel("Số phim")
    st.pyplot(fig)

# 📈 **Biểu đồ điểm trung bình theo năm**
with col2:
    st.subheader("📈 Điểm trung bình mỗi năm")
    fig, ax = plt.subplots(figsize=(8, 4))
    filtered_df.groupby("year")["vote_average"].mean().plot(kind="line", ax=ax, marker="o", color="orange")
    ax.set_ylabel("Điểm trung bình")
    st.pyplot(fig)

# --- **DANH SÁCH PHIM** ---
st.subheader("🎥 Danh sách phim")

for index, row in filtered_df.iterrows():
    col1, col2 = st.columns([1, 4])

    with col1:
        if pd.notna(row["poster_path"]):
            st.image(f"https://image.tmdb.org/t/p/w200{row['poster_path']}", width=120)
        else:
            st.image("https://via.placeholder.com/120x180?text=No+Image", width=120)

    with col2:
        st.markdown(f"### {row['title']} ({row['year']})")
        st.write(f"⭐ **{row['vote_average']}**")
        st.write(row['overview'])

    st.markdown("---")
