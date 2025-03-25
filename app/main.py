from fastapi import Depends, FastAPI

from app.api import products, products, users
from app.auth.dependencies import get_current_user


app = FastAPI(title="Order Management System", version="1.0")

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"], dependencies=[Depends(get_current_user)])
