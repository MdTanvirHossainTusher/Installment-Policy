from fastapi import APIRouter, Header
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.schemas.customer_schema import CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse, LoginRequest, OTPVerificationRequest, EmailRequest
from app.services.customer_service import CustomerService


router = APIRouter(prefix="/auth", tags=["Auth APIs"])

db_session = Depends(get_db)
security = HTTPBasic()

@router.post("/register")
async def create_customer(customer: CustomerCreateRequest, db: Session = db_session):
    return CustomerService(db).create_customer(customer)

@router.post("/verify_otp")
async def verify_otp(verification: OTPVerificationRequest, db: Session = db_session):
    return CustomerService(db).verify_otp(verification.email, verification.otp)

@router.post("/resend_otp")
async def resend_otp(email_request: EmailRequest, db: Session = db_session):
    return CustomerService(db).resend_otp(email_request.email)

@router.post("/login")
async def login_customer(credentials: HTTPBasicCredentials = Depends(security), db: Session = db_session):
    return CustomerService(db).login_customer_using_basic_auth(credentials)

@router.post("/logout")
async def logout_customer(authorization: str = Header(...), db: Session = db_session):
    return CustomerService(db).logout_customer(authorization)