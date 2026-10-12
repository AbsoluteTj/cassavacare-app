from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_password_hash
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])


# Skema Pydantic untuk validasi input registrasi (jika belum ada di models.py)
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # 1. Cek apakah email sudah terdaftar di database
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email sudah terdaftar"
        )

    # 2. Hash password pengguna menggunakan fungsi dari auth.py
    hashed_password = get_password_hash(user_data.password)

    # 3. Buat instance model User baru (sesuaikan field dengan models.py Anda)
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_password,
    )

    # 4. Simpan ke database MySQL XAMPP
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registrasi berhasil",
        "user": {
            "id": new_user.id,
            "full_name": new_user.full_name,
            "email": new_user.email
        }
    }