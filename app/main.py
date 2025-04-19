from fastapi import FastAPI
from app.database import engine
from app.database import Base
from app.routes import admin_route, customer_route, auth_route, product_route, category_route, cart_item_route, email_route, logged_user_route
from app.authorization import RBACMiddleware
from app.scheduler import start_scheduler
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*", "http://127.0.0.1:5500", "http://localhost:5500", "http://localhost:3000"],
#     # allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(RBACMiddleware)

app.include_router(customer_route.router)
app.include_router(auth_route.router)
app.include_router(product_route.router)
app.include_router(category_route.router)
app.include_router(cart_item_route.router)
app.include_router(email_route.router)
app.include_router(admin_route.router)
app.include_router(logged_user_route.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
def startup_event():
    scheduler = start_scheduler()
    app.state.scheduler = scheduler

@app.on_event("shutdown")
def shutdown_event():
    app.state.scheduler.shutdown()