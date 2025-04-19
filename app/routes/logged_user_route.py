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

router = APIRouter(prefix="/current-logged-in-user-details", tags=["Current User API"])

@router.get("")
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
