from fastapi import FastAPI
from app.database import engine
from app.database import Base
from app.routes import customer_route, auth_route
from app.authorization import RBACMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(RBACMiddleware)

app.include_router(customer_route.router)
app.include_router(auth_route.router)