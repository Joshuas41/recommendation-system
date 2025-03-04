from sqlalchemy import create_engine

# Thay 'yourpassword' bằng mật khẩu của bạn
DATABASE_URL = "postgresql://postgres:Anhkha1@localhost:5432/recommendation_db"

# Kết nối đến PostgreSQL
engine = create_engine(DATABASE_URL)

# Kiểm tra kết nối
try:
    with engine.connect() as conn:
        print("✅ Kết nối PostgreSQL thành công!")
except Exception as e:
    print("❌ Lỗi kết nối:", e)
