from fastapi import APIRouter, Header, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.models.models import UserSession
from app.schemas.customer_schema import CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse, LoginRequest, OTPVerificationRequest, EmailRequest
from app.services.customer_service import CustomerService
from app.models.models import Customer
from datetime import datetime


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

# @router.post("/me/role")
# async def get_logged_in_user(
#     authorization: str = Header(...),
#     db: Session = db_session
# ):
#     if not authorization or not authorization.startswith("Bearer "):
#         return JSONResponse(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             content={"detail": "Authorization token missing or invalid"}
#         )
#
#     token = authorization.split(" ")[1]
#     session = db.query(UserSession).filter(
#         UserSession.id == token,
#         UserSession.is_active == True,
#         UserSession.expires_at > datetime.now()
#     ).first()
#
#     if not session:
#         return JSONResponse(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             content={"detail": "Session expired or invalid"}
#         )
#
#     customer = db.query(Customer).filter(
#         Customer.id == session.customer_id,
#         Customer.deleted == False
#     ).first()
#
#     if not customer:
#         return JSONResponse(
#             status_code=status.HTTP_404_NOT_FOUND,
#             content={"detail": "Customer not found"}
#         )
#     return {
#         "id": customer.id,
#         "name": customer.name,
#         "email": customer.email,
#         "role": customer.role.value
#     }