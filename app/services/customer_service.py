from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models.customer import Customer
from fastapi import HTTPException
from passlib.context import CryptContext
from app.schemas.customer_schema import CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse
import datetime
import logging
import smtplib
import os
from pydantic import EmailStr
from email.message import EmailMessage
from dotenv import load_dotenv

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

    def get_all_customers(self):
        try:
            return self.db.query(Customer).filter(Customer.deleted == False).all()
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
            logger.info(f"Creating customer with email: {email}")
            self.check_if_locked(email)
            existing_customer = self.db.query(Customer).filter(Customer.email == email, Customer.deleted == False).first()
            if existing_customer:
                raise HTTPException(
                    status_code=400,
                    detail=f"Customer with email {email} already exists"
                )
            if email not in CustomerService.otp_attempts:
                logger.info(f"New customer with email: {email}")
                logger.info(f'Otp attempts before init: {CustomerService.otp_attempts}')
                CustomerService.otp_attempts[email] = 0
                logger.info(f'Otp attempts after init: {CustomerService.otp_attempts}')

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

    def update_customer(self, customer_id: int, updated_customer: CustomerUpdateRequest):
        try:
            customer = self.db.query(Customer).filter(Customer.id == customer_id, Customer.deleted == False).first()
            if customer is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"customer with ID: {customer_id} does not exist"
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
        logger.info(f'OTP message is {msg}')

        server.send_message(msg)
        server.quit()
        return "OTP sent successfully"
    

    # def verify_otp(self, email: EmailStr, entered_otp: str, password: str = None):
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

