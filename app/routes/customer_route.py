from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from app.schemas.customer_schema import CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse
from app.services.customer_service import CustomerService


router = APIRouter(prefix="/customers", tags=["Customer APIs"])

@router.get("/")
async def index():
    return {"message": "Hello from installment policy API"}


@router.get("", response_model=list[CustomerResponse])
async def get_all_customers(db: Session = Depends(get_db)):
    return CustomerService(db).get_all_customers()


@router.get("/{customer_id}")
async def get_customer(customer_id: int, db: Session = Depends(get_db), response_model=CustomerResponse):
    return CustomerService(db).get_customer_by_id(customer_id)


@router.post("")
async def create_customer(customer: CustomerCreateRequest, db: Session = Depends(get_db)):
    return CustomerService(db).create_customer(customer)


@router.put("/{customer_id}")
async def update_customer(customer_id: int, updated_customer: CustomerUpdateRequest, db: Session = Depends(get_db), response_model=CustomerResponse):
    return CustomerService(db).update_customer(customer_id, updated_customer)


@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    return CustomerService(db).delete_customer(customer_id)