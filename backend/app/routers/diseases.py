from fastapi import APIRouter, Depends
from models import DiseaseCreate, SingleDiseaseResponse, ListDiseaseResponse, ResponseMeta, DiseaseResponse
import uuid
from datetime import datetime
from auth_utils import get_current_user

router = APIRouter()

@router.get("", response_model=ListDiseaseResponse)
def list_diseases():
    return ListDiseaseResponse(meta=ResponseMeta(code=200, message="OK"), data=[])

@router.post("", response_model=SingleDiseaseResponse, status_code=201)
def create_disease(disease: DiseaseCreate, current_user = Depends(get_current_user)):
    d = DiseaseResponse(**disease.model_dump(), id=uuid.uuid4(), created_at=datetime.now(), updated_at=datetime.now())
    return SingleDiseaseResponse(meta=ResponseMeta(code=201, message="Created"), data=d)
