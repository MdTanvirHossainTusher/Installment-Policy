from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from app.services.product_service import ProductService
from datetime import datetime, timedelta


router = APIRouter(prefix="/admin", tags=["Report APIs"])

db_session = Depends(get_db)

@router.post("/reports/generate")
async def create_report(type: str = 'csv', weekly: bool = True, db: Session = db_session):
    if type not in ['csv', 'json']:
        return {"error": "Invalid report type. Choose either 'csv' or 'json'."}
    
    if weekly: target_date = datetime.now() - timedelta(days=7)
    else: target_date = datetime.now() - timedelta(days=30)

    start = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    end = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
    # start = datetime(2025, 5, 13, 0, 0, 0)
    # end = datetime(2025, 5, 20, 23, 59, 59)
    data = ProductService(db).get_report_data(start, end)
    
    if type == 'csv': return ProductService(db).generate_csv_report(data)
    else: return ProductService(db).generate_json_report(data)


@router.get("/search")
async def search_anything(query: str, db: Session = db_session):
    return ProductService(db).search_cart_items(query)