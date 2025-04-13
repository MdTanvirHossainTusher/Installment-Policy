from fastapi import FastAPI
from app.database import engine
from app.database import Base
from app.routes import customer_route

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(customer_route.router)