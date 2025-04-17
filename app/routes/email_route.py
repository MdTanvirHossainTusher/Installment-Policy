from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from app.services.email_service import EmailService

router = APIRouter(prefix="/emails", tags=["Email APIs"])


@router.get("/test-email")
def test_email(db: Session = Depends(get_db)):

    email_service = EmailService()
    result = email_service.send_email_for_installment_due(
        receiver_email="beast.reign10@gmail.com",
        customer_name="Test Customer",
        amount=100.00,
        due_date="2025-04-20",
        product_name="Test Product"
    )
    return {"status": "email sent", "result": result}