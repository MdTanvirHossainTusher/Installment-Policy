from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends


router = APIRouter(prefix="/customers", tags=["Customer APIs"])


@router.get("/")
async def index():
    return {"message": "Hello from installment policy API"}