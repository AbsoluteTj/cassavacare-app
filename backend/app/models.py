import enum
import uuid
import re
from datetime import datetime
from typing import List, Optional, Any, Dict

from pydantic import BaseModel, Field, ConfigDict, field_validator
from sqlalchemy import Column, String, Boolean, Float, Text, DateTime, Enum as SQLEnum, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
Base = declarative_base()

class UserRole(str, enum.Enum):
    FARMER = "FARMER"
    EXPERT = "EXPERT"
    ADMIN = "ADMIN"

class PredictionStatus(str, enum.Enum):
    CONFIDENT = "CONFIDENT"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    FAILED = "FAILED"

class DiseaseCode(str, enum.Enum):
    CMD = "CMD"
    CBSD = "CBSD"
    BLS = "BLS"
    GMD = "GMD"
    RMD = "RMD"
    HEALTHY = "HEALTHY"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole, name="user_role_enum"), nullable=False, default=UserRole.FARMER)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    is_revoked = Column(Boolean, nullable=False, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    user = relationship("User", back_populates="refresh_tokens")

class Disease(Base):
    __tablename__ = "diseases"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    latin_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    symptoms = Column(Text, nullable=False)
    treatment = Column(Text, nullable=False)
    prevention = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    predictions = relationship("Prediction", back_populates="disease")

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    disease_id = Column(UUID(as_uuid=True), ForeignKey("diseases.id", ondelete="SET NULL"), nullable=True)
    image_url = Column(String(512), nullable=False)
    predicted_label = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=False)
    status = Column(SQLEnum(PredictionStatus, name="prediction_status_enum"), nullable=False)
    metadata_json = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (Index("idx_predictions_user_created", "user_id", created_at.desc()),)
    user = relationship("User", back_populates="predictions")
    disease = relationship("Disease", back_populates="disease")

class ResponseMeta(BaseModel):
    code: int
    message: str

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int

class UserSignUpRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    role: UserRole = UserRole.FARMER

class UserLoginRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX)
    password: str

class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int

class UserResponseData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

class AuthResponse(BaseModel):
    meta: ResponseMeta
    data: Dict[str, Any]

class DiseaseBase(BaseModel):
    code: str
    name: str
    latin_name: Optional[str] = None
    description: str
    symptoms: str
    treatment: str
    prevention: str

class DiseaseCreate(DiseaseBase): pass

class DiseaseResponse(DiseaseBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class SingleDiseaseResponse(BaseModel):
    meta: ResponseMeta
    data: DiseaseResponse

class ListDiseaseResponse(BaseModel):
    meta: ResponseMeta
    data: List[DiseaseResponse]

class PredictionDetailData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    disease_id: Optional[uuid.UUID] = None
    image_url: str
    predicted_label: str
    confidence_score: float
    status: PredictionStatus
    metadata_json: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    created_at: datetime
    disease_info: Optional[DiseaseResponse] = None

class FallbackWarning(BaseModel):
    threshold_applied: float = 0.70
    user_message: str = "Hasil diagnosa memiliki tingkat kepastian di bawah 70%. Harap ambil ulang foto daun dengan pencahayaan terang dan fokus yang jelas."
    suggested_actions: List[str] = ["Pastikan daun memenuhi 80% area foto", "Gunakan latar belakang netral", "Konsultasikan ke PPL/Pakar"]

class PredictionResponse(BaseModel):
    meta: ResponseMeta
    data: PredictionDetailData
    warning: Optional[FallbackWarning] = None

class ListPredictionResponse(BaseModel):
    meta: ResponseMeta
    data: List[PredictionDetailData]
    pagination: PaginationMeta
