from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models.customer import Customer
from fastapi import HTTPException
from passlib.context import CryptContext
from app.schemas.customer_schema import CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse
import logging

logger = logging.getLogger(__name__)

class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        self.otp = None

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
            # return CustomerResponse(
            #     id=customer.id,
            #     name=customer.name,
            #     email=customer.email,
            #     mobile=customer.mobile,
            #     role=customer.role
            # )

        except SQLAlchemyError as e:
            logger.error(f"Error retrieving customer: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving customer: {str(e)}"
            )

    def create_customer(self, customer: CustomerCreateRequest):
        try:
            existing_customer = self.db.query(Customer).filter(Customer.email == customer.email, Customer.deleted == False).first()
            if existing_customer:
                raise HTTPException(
                    status_code=400,
                    detail=f"Customer with email {customer.email} already exists"
                )
           
            self.send_otp(customer.email)

            if(self.verify_otp()):
                log.info(f"OTP verified successfully for {customer.email}")
                new_customer = Customer()
                if customer.email is not None: new_customer.email = customer.email
                if customer.password is not None: new_customer.password = self.bcrypt_context.hash(customer.password)

                self.db.add(new_customer)
                self.db.commit()
                self.db.refresh(new_customer)
                return CustomerResponse(**new_customer.__dict__)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid OTP"
                )

            # self.db.add(new_customer)
            # self.db.commit()
            # self.db.refresh(new_customer)

            # return CustomerResponse(**new_customer.__dict__)

        except SQLAlchemyError as e:
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
            # self.db.delete(customer)
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

    def generate_otp(self):
        import random
        otp = str(random.randint(100000, 999999))
        return otp

    def send_otp(self, input_email):
        import smtplib
        from email.message import EmailMessage
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        self.otp = self.generate_otp()

        from_mail = 'mohammedtusher1999@gmail.com'
        server.login(from_mail, 'ehsv vlur yevq fepl')

        msg = EmailMessage()
        msg['Subject'] = 'OTP Verification' 
        msg['From'] = from_mail
        msg['To'] = input_email
        # msg.set_content(f'Your OTP is {otp}')
        msg.set_content(f'Your OTP is {self.otp}')

        server.send_message(msg)
        # server.quit()
        return "OTP sent successfully"
    
    def verify_otp(self, entered_otp):
        return entered_otp == self.otp
