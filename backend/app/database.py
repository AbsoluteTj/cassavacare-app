import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Memuat variabel dari file .env
load_dotenv()

# Mengambil variabel DATABASE_URL dari .env atau default ke XAMPP lokal
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://root:@localhost:3306/cassavacare_db"
)

# Membuat engine database SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Membuat konfigurasi SessionLocal untuk operasi database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class wajib untuk pembuatan model ORM (digunakan di models.py)
Base = declarative_base()

# Dependency FastAPI untuk mengelola sesi database per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()