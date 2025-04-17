from fastapi import FastAPI
from app.database import engine
from app.database import Base
from app.routes import customer_route, auth_route, product_route, category_route, cart_item_route
from app.authorization import RBACMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(RBACMiddleware)

app.include_router(customer_route.router)
app.include_router(auth_route.router)
app.include_router(product_route.router)
app.include_router(category_route.router)
app.include_router(cart_item_route.router)