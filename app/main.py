from fastapi import FastAPI
from app.database import engine
from app.database import Base
from app.routes import customer_route, auth_route, product_route, category_route, cart_item_route, email_route, report_route
from app.authorization import RBACMiddleware
from app.scheduler import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(RBACMiddleware)

app.include_router(customer_route.router)
app.include_router(auth_route.router)
app.include_router(product_route.router)
app.include_router(category_route.router)
app.include_router(cart_item_route.router)
app.include_router(email_route.router)
app.include_router(report_route.router)

@app.on_event("startup")
def startup_event():
    scheduler = start_scheduler()
    app.state.scheduler = scheduler

@app.on_event("shutdown")
def shutdown_event():
    app.state.scheduler.shutdown()