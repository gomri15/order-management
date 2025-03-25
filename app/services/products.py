# app/services/product_service.py

from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status

from app.db.models import Product
from app.schemas.products import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def create_product(self, product_data: ProductCreate) -> Product:
        product = Product(**product_data.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_product(self, product_id: UUID) -> Product:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    def update_product(self, product_id: UUID, updates: ProductUpdate) -> Product:
        product = self.get_product(product_id)
        for key, value in updates.model_dump(exclude_unset=True).items():
            setattr(product, key, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete_product(self, product_id: UUID) -> None:
        product = self.get_product(product_id)
        self.db.delete(product)
        self.db.commit()

    def list_products(self) -> list[Product]:
        return self.db.query(Product).all()
