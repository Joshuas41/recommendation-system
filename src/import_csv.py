import pandas as pd
from sqlalchemy import create_engine

# Thay 'yourpassword' bằng mật khẩu PostgreSQL của bạn
DATABASE_URL = "postgresql://postgres:Anhkha1@localhost:5432/recommendation_db"

# Kết nối đến PostgreSQL
engine = create_engine(DATABASE_URL)

# Đọc file CSV
df = pd.read_csv("data/movies.csv")

# Ghi dữ liệu vào bảng movies
df.to_sql("movies", engine, if_exists="append", index=False)

print("✅ Dữ liệu đã được nhập vào bảng movies thành công!")
