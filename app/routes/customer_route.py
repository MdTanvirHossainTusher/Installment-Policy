from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from app.schemas.customer_schema import CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse, OTPVerificationRequest, EmailRequest
from app.services.customer_service import CustomerService
from fastapi_pagination import Page, add_pagination
from app.models.pagination import PaginationParams

router = APIRouter(prefix="/customers", tags=["Customer APIs"])

add_pagination(router)


@router.get("", response_model=Page[CustomerResponse])
async def get_all_customers(pagination: PaginationParams = Depends(), db: Session = Depends(get_db)):
    return CustomerService(db).get_all_customers(pagination)


@router.get("/{customer_id}")
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return CustomerService(db).get_customer_by_id(customer_id)


@router.put("/{customer_id}")
async def update_customer(customer_id: int, updated_customer: CustomerUpdateRequest, db: Session = Depends(get_db)):
    return CustomerService(db).update_customer(customer_id, updated_customer)


@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    return CustomerService(db).delete_customer(customer_id)

# @router.post("")
# async def create_customer(customer: CustomerCreateRequest, db: Session = Depends(get_db)):
#     return CustomerService(db).create_customer(customer)

# @router.post("/verify_otp")
# async def verify_otp(verification: OTPVerificationRequest, db: Session = Depends(get_db)):
#     return CustomerService(db).verify_otp(verification.email, verification.otp)

# @router.post("/resend_otp")
# async def resend_otp(email_request: EmailRequest, db: Session = Depends(get_db)):
#     return CustomerService(db).resend_otp(email_request.email)
