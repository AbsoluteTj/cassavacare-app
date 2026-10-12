from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from models import PredictionResponse, ResponseMeta, PredictionDetailData, PredictionStatus, FallbackWarning
import uuid
from datetime import datetime
from auth_utils import get_current_user
import random

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB
ALLOWED_TYPES = ["image/jpeg", "image/png"]

@router.post("", response_model=PredictionResponse, status_code=201)
async def predict_disease(image: UploadFile = File(...), current_user = Depends(get_current_user)):
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG/PNG allowed.")
    
    content = await image.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max 5MB.")
    
    # Dummy AI Logic
    confidence = random.uniform(0.5, 0.99)
    status = PredictionStatus.CONFIDENT if confidence >= 0.70 else PredictionStatus.LOW_CONFIDENCE
    
    pred_data = PredictionDetailData(
        id=uuid.uuid4(), user_id=current_user["id"],
        image_url="https://storage.cassavacare.id/mock.jpg",
        predicted_label="CMD" if status == PredictionStatus.CONFIDENT else "UNKNOWN",
        confidence_score=confidence, status=status, created_at=datetime.now()
    )
    
    warning = FallbackWarning() if status == PredictionStatus.LOW_CONFIDENCE else None
    
    return PredictionResponse(
        meta=ResponseMeta(code=201, message="Diagnosa AI berhasil diproses"),
        data=pred_data,
        warning=warning
    )
