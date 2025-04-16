from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.customer import UserSession, Customer
from fastapi import UploadFile, File
import os
import shutil
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

# UPLOAD_DIR = os.getenv("PRODUCT_IMAGES_DIR", "app/static/uploads")
# os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    

# class FileUtils:

#     @staticmethod
#     async def save_product_image(image_file: UploadFile) -> str:
#         file_extension = os.path.splitext(image_file.filename)[1]
#         unique_filename = f"{uuid4()}{file_extension}"

#         file_path = os.path.join(UPLOAD_DIR, unique_filename)

#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(image_file.file, buffer)

#         # return f"/product_images/{unique_filename}"
#         return f"{UPLOAD_DIR}/{unique_filename}"