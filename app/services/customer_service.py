import uuid
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.enums.roles import Roles
from app.models.models import Customer, UserSession
from fastapi import HTTPException
from passlib.context import CryptContext
from app.schemas.customer_schema import CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse, LoginRequest
from datetime import datetime, timedelta
import logging
import smtplib
import os
from pydantic import EmailStr
from email.message import EmailMessage
from dotenv import load_dotenv
from fastapi_pagination import Page
from app.schemas.pagination_schema import PaginationParams
from sqlalchemy import desc, asc
from fastapi.security import HTTPBasicCredentials
from starlette import status

logger = logging.getLogger(__name__)

load_dotenv()

class CustomerService:
    otps = {}
    otp_attempts = {}
    locked_users = {}
    user_passwords = {}

    def __init__(self, db: Session):
        self.db = db
        self.bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


    def get_all_customers(self, pagination: PaginationParams):
        try:
            query = self.db.query(Customer).filter(Customer.deleted == False)

            if pagination.sort_by:
                if hasattr(Customer, str(pagination.sort_by)):
                    sort_column = getattr(Customer, str(pagination.sort_by))
                    if pagination.sort_dir and pagination.sort_dir.lower() == 'desc':
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(sort_column)
            else:
                query = query.order_by(asc(Customer.id))

            total_items = query.count()
            size = int(pagination.size)
            total_pages = (total_items + size - 1) // size if size > 0 else 0
            page = int(pagination.page)
            query = query.offset((page - 1) * size).limit(size)

            customers = query.all()
            customer_responses = [CustomerResponse(**customer.__dict__) for customer in customers]

            return Page[CustomerResponse](
                items=customer_responses,
                total=total_items,
                page=page,
                size=size,
                pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )
        except SQLAlchemyError as e:
            logger.error(f"Error fetching customers: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching customers: {str(e)}")


    def get_customer_by_id(self, customer_id: int):
        try:
            customer = self.db.query(Customer).filter(Customer.id == customer_id, Customer.deleted == False).first()
            if customer is None:
                raise HTTPException(status_code=400, detail=f"customer with ID: {customer_id} does not exist")
            return CustomerResponse(**customer.__dict__)

        except SQLAlchemyError as e:
            logger.error(f"Error retrieving customer: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving customer: {str(e)}"
            )


    def create_customer(self, customer: CustomerCreateRequest):
        try:
            email = customer.email
            self.check_if_locked(email)
            existing_customer = self.db.query(Customer).filter(Customer.email == email, Customer.deleted == False).first()
            if existing_customer:
                raise HTTPException(
                    status_code=400,
                    detail=f"Customer with email {email} already exists"
                )
            if email not in CustomerService.otp_attempts:
                CustomerService.otp_attempts[email] = 0

            CustomerService.user_passwords[email] = customer.password
            self.send_otp(email)
            return {"message": "OTP sent successfully. Please verify to complete registration."}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating customer: {str(e)}"
            )


    def update_customer(self, customer_id: int, updated_customer: CustomerUpdateRequest, current_user_id: int):
        try:
            current_user = self.db.query(Customer).filter(Customer.id == current_user_id, Customer.deleted == False).first()
        
            if current_user.id != customer_id and current_user.role != Roles.ADMIN:
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to update this customer's information"
                )
            
            customer = self.db.query(Customer).filter(Customer.id == customer_id, Customer.deleted == False).first()
            if customer is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Customer with ID: {customer_id} does not exist"
                )
            
            if updated_customer.name is not None: customer.name = str(updated_customer.name)
            if updated_customer.password is not None: customer.password = self.bcrypt_context.hash(updated_customer.password)
            if updated_customer.mobile is not None: customer.mobile = updated_customer.mobile

            self.db.add(customer)
            self.db.commit()
            self.db.refresh(customer)

            return CustomerResponse(**customer.__dict__)

        except SQLAlchemyError as e:
            logger.error(f"Error updating customer: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error updating customer: {str(e)}"
            )

    def delete_customer(self, customer_id: int):
        try:
            customer = self.db.query(Customer).filter(Customer.id == customer_id, Customer.deleted == False).first()
            if customer is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"customer with ID: {customer_id} does not exist"
                )
            customer.deleted = True
            self.db.commit()
            self.db.refresh(customer)
            return {"message": "Customer deleted successfully"}

        except SQLAlchemyError as e:
            logger.error(f"Error deleting customer: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting customer: {str(e)}"
            )

    def check_if_locked(self, email: EmailStr):
        if email in CustomerService.locked_users:
            lock_time = CustomerService.locked_users[email]
            current_time = datetime.datetime.now()
            if (current_time - lock_time).total_seconds() < int(os.getenv('OTP_LOCK_TIME', 300)):
                remaining_seconds = int(os.getenv('OTP_LOCK_TIME', 300)) - int((current_time - lock_time).total_seconds())
                remaining_minutes = remaining_seconds // 60
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many failed attempts. Please try again after {remaining_minutes} minutes."
                )
            else:
                del CustomerService.locked_users[email]
                CustomerService.otp_attempts[email] = 0

    def generate_otp(self):
        import random
        otp = str(random.randint(100000, 999999))
        return otp

    def send_otp(self, input_email):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        otp = self.generate_otp()
        CustomerService.otps[input_email] = otp

        from_mail = os.getenv('OTP_FROM_EMAIL')
        server.login(from_mail, os.getenv('APPLICATION_PASSWORD'))

        msg = EmailMessage()
        msg['Subject'] = os.getenv('OTP_EMAIL_SUBJECT')
        msg['From'] = from_mail
        msg['To'] = input_email
        msg.set_content(os.getenv('OTP_EMAIL_BODY').format(otp=otp))

        server.send_message(msg)
        server.quit()
        return "OTP sent successfully"
    

    def verify_otp(self, email: EmailStr, entered_otp: str, password: str = None):
        self.check_if_locked(email)

        if email not in CustomerService.otp_attempts:
            CustomerService.otp_attempts[email] = 0

        if email not in CustomerService.otps:
            raise HTTPException(
                status_code=400,
                detail="No OTP has been sent to this email. Please request an OTP first."
            )
        
        if entered_otp != CustomerService.otps[email]:
            CustomerService.otp_attempts[email] += 1
                
            if CustomerService.otp_attempts[email] >= 3:
                CustomerService.locked_users[email] = datetime.datetime.now()
                raise HTTPException(
                    status_code=429,
                    detail="Too many failed attempts. Your account is locked for 5 minutes."
                )
            
            remaining_attempts = 3 - CustomerService.otp_attempts[email]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid OTP. {remaining_attempts} attempts remaining."
            )

        CustomerService.otp_attempts[email] = 0

        if password is None:
            password = CustomerService.user_passwords[email]

        if password:
            try:
                existing_customer = self.db.query(Customer).filter(Customer.email == email, Customer.deleted == False).first()
                if existing_customer:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Customer with email {email} already exists"
                    )
                new_customer = Customer()
                new_customer.email = email
                new_customer.password = self.bcrypt_context.hash(password)

                self.db.add(new_customer)
                self.db.commit()
                self.db.refresh(new_customer)

                if email in CustomerService.otps:
                    del CustomerService.otps[email]
                if email in CustomerService.user_passwords:
                    del CustomerService.user_passwords[email]

                return CustomerResponse(**new_customer.__dict__)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error creating customer: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error creating customer: {str(e)}"
                )
        
        self.otp_attempts[email] = 0
        return {"message": "OTP verified successfully"}
    
    
    def resend_otp(self, email: EmailStr):
        self.check_if_locked(email)
        self.send_otp(email)
        return {"message": "OTP resent successfully"}
    

    def login_customer(self, customer: LoginRequest):
        email = customer.email

        existing_customer = self.db.query(Customer).filter(Customer.email == email, Customer.deleted == False).first()
        if not existing_customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Enter valid email"
            )
        if not self.bcrypt_context.verify(customer.password, existing_customer.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
        return {"message": "Login successful"}
    
    def login_customer_using_basic_auth(self, credentials: HTTPBasicCredentials):
        email = credentials.username
        password = credentials.password

        existing_customer = self.db.query(Customer).filter(Customer.email == email, Customer.deleted == False).first()

        already_logged_in = self.db.query(UserSession).filter(UserSession.customer_id == existing_customer.id, UserSession.is_active == True).first()
        if already_logged_in:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are already logged in"
            )

        if not existing_customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Enter valid email"
            )
        if not self.bcrypt_context.verify(password, existing_customer.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
        session_token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=24)
        
        new_session = UserSession(id=session_token, customer_id=existing_customer.id, expires_at=expires_at, is_active=True)
        
        try:
            self.db.add(new_session)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to create session"
            )
        return {
            "message": "Login successful",
            "session_token": session_token,
            "expires_at": expires_at
        }
    

    def logout_customer(self, token: str):
        if not token or not token.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token header",
            )
        token = token.split(" ")[1]
        session = self.db.query(UserSession).filter(UserSession.id == token, UserSession.is_active == True, 
                                                    UserSession.expires_at > datetime.now()).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session",
            )
        try:
            session.is_active = False
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error invalidating session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to logout"
            )
        return {"message": "Logout successful"}

