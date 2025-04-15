from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.customer import UserSession, Customer


security = HTTPBearer()

class AuthUtils:

    @staticmethod
    async def get_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> int:

        token = credentials.credentials
        
        session = db.query(UserSession).filter(
            UserSession.id == token, UserSession.is_active == True, UserSession.expires_at > datetime.now()
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )
        return session.customer_id
    
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> Customer:
        
        current_user_id = await AuthUtils.get_current_user_id(credentials, db)
        user = db.query(Customer).filter(Customer.id == current_user_id, Customer.deleted == False).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user