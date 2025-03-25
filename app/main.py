from fastapi import FastAPI

from app.api import products, users


app = FastAPI(title="Order Management System", version="1.0")

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"])
