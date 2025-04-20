from typing import Optional
from fastapi import Request, status, Header, Depends
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from app.models.models import UserSession, Customer
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
import fnmatch

RESOURCES_FOR_ROLES = {
    'admin': {
        '/': ['read'],
        '/customers': ['read', 'write', 'update', 'delete'],
        '/customers/#/me': ['read', 'write', 'update', 'delete'],
        '/customers/**': ['read', 'write', 'update', 'delete'],
        '/auth/me': ['read', 'write', 'update', 'delete'],
        '/auth/register': ['write'],
        '/auth/verify_otp': ['write'],
        '/auth/resend_otp': ['write'],
        '/auth/login': ['write'],
        '/auth/logout': ['write'],
        '/products': ['read', 'write', 'update', 'delete'],
        '/products/**': ['read', 'write', 'update', 'delete'],
        '/categories': ['read', 'write', 'update', 'delete'],
        '/categories/**': ['read', 'write', 'update', 'delete'],
        '/carts/**': ['read', 'write', 'update', 'delete'],
        '/emails/test-email': ['read', 'write', 'update', 'delete'],
        '/admin/**': ['read', 'write', 'update', 'delete'],
        '/auth/me/role': ['read', 'write', 'update', 'delete'],
        '/auth/**': ['read'],
        '/auth/*': ['read'],
        '/auth/bal': ['read'],
        '/me': ['read', 'write', 'update', 'delete'],
        '/current-logged-in-user-details': ['read', 'write', 'update', 'delete'],
    },
    'user': {
        '/': ['read'],
        '/customers': ['read'],
        '/customers/**': ['read', 'update'],
        '/auth/register': ['write'],
        '/auth/verify_otp': ['write'],
        '/auth/resend_otp': ['write'],
        '/auth/login': ['write'],
        '/auth/logout': ['write'],
        '/products': ['read'],
        '/products/**': ['read', 'write'],
        '/categories': ['read'],
        '/categories/**': ['read'],
        '/carts/**': ['read', 'write', 'update', 'delete'],
        '/auth/me': ['read', 'write', 'update', 'delete'],
        '/auth/**': ['read'],
        '/auth/*': ['read'],
        '/customers/logged-in-user/#': ['read', 'write', 'update', 'delete'],
        '/me': ['read', 'write', 'update', 'delete'],
        '/current-logged-in-user-details': ['read', 'write', 'update', 'delete'],
        # '/emails/test-email': ['read', 'write', 'update', 'delete'],
    }
}

# EXCLUDED_PATHS = ['/', '/docs', '/openapi.json', '/auth/register', '/auth/login', '/auth/verify_otp', '/auth/resend_otp', '/auth/me']

EXCLUDED_PATHS = [
    '/',
    '/index.html',  
    '/register.html', 
    '/home.html',       
    '/static/*',
    '/favicon.ico',
    '/docs',
    '/openapi.json',
    '/auth/register',
    '/auth/login',
    '/auth/verify_otp',
    '/auth/resend_otp',
    '/auth/me'
]

def translate_method_to_action(method: str) -> str:
    method_permission_mapping = {
        'GET': 'read',
        'POST': 'write',
        'PUT': 'update',
        'DELETE': 'delete',
    }
    return method_permission_mapping.get(method.upper(), 'read')


def has_permission(user_role, resource_name, required_permission):
    if user_role not in RESOURCES_FOR_ROLES:
        return False
    role_permissions = RESOURCES_FOR_ROLES[user_role]

    for pattern, actions in role_permissions.items():
        if fnmatch.fnmatch(resource_name, pattern):
            return required_permission in actions
    return False


async def get_current_user_role(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    return await get_user_role_from_token(authorization, db)


async def get_user_role_from_token(authorization, db):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split(" ")[1]
    session = db.query(UserSession).filter(
        UserSession.id == token, 
        UserSession.is_active == True, 
        UserSession.expires_at > datetime.now()
    ).first()
    
    if not session:
        return None
    
    customer = db.query(Customer).filter(Customer.id == session.customer_id, Customer.deleted == False).first()
    if not customer:
        return None
    
    return customer.role.value

class RBACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in ['', '/']:
            return await call_next(request)
        
        for excluded in EXCLUDED_PATHS:
            if fnmatch.fnmatch(path, excluded):
                return await call_next(request)

        for excluded in EXCLUDED_PATHS:
            if path == excluded:
                return await call_next(request)

        resource = path
        request_method = request.method
        required_permission = translate_method_to_action(request_method)
        
        authorization = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing"}
            )
        db = SessionLocal()
        
        try:
            user_role = await get_user_role_from_token(authorization, db)
            
            if not user_role or not has_permission(user_role, resource, required_permission):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Insufficient permissions"}
                )
            
            return await call_next(request)
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"RBAC error: {str(e)}"}
            )
        finally:
            db.close()