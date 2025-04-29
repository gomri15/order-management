from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import orders, products, users
from app.auth.dependencies import get_current_user

app = FastAPI(title="Order Management System", version="1.0", root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 allows all origins
    allow_credentials=True,  # needed if sending cookies or Authorization headers
    allow_methods=["*"],  # GET, POST, DELETE, etc.
    allow_headers=["*"],  # Accept, Authorization, Content-Type, etc.
)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"], dependencies=[Depends(get_current_user)])
app.include_router(orders.router, prefix="/orders", tags=["Orders"], dependencies=[Depends(get_current_user)])
