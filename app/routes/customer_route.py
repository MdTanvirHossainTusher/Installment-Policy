from fastapi_pagination import Page, add_pagination
from app.schemas.pagination_schema import PaginationParams
from fastapi import APIRouter, Header, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
from app.models.models import UserSession
from app.schemas.customer_schema import CustomerUpdateRequest, CustomerResponse
from app.services.customer_service import CustomerService
from app.models.models import Customer
from datetime import datetime
from app.utils import AuthUtils

router = APIRouter(prefix="/customers", tags=["Customer APIs"])

add_pagination(router)

@router.get("/#/me")
async def get_logged_in_user(
        authorization: str = Header(None),
        db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Authorization token missing or invalid"}
        )

    token = authorization.split(" ")[1]
    session = db.query(UserSession).filter(
        UserSession.id == token,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.now()
    ).first()

    if not session:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Session expired or invalid"}
        )

    customer = db.query(Customer).filter(
        Customer.id == session.customer_id,
        Customer.deleted == False
    ).first()

    if not customer:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Customer not found"}
        )

    return {
        "role": customer.role.value
    }


@router.get("", response_model=Page[CustomerResponse])
async def get_all_customers(pagination: PaginationParams = Depends(), db: Session = Depends(get_db)):
    return CustomerService(db).get_all_customers(pagination)


@router.get("/{customer_id}")
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return CustomerService(db).get_customer_by_id(customer_id)


@router.put("/{customer_id}")
async def update_customer(customer_id: int, updated_customer: CustomerUpdateRequest, 
                        current_user_id: int = Depends(AuthUtils.get_current_user_id), 
                        db: Session = Depends(get_db)):
    return CustomerService(db).update_customer(customer_id, updated_customer, current_user_id)


@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    return CustomerService(db).delete_customer(customer_id)


