import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.db.database import get_db
from app.schemas.products import ProductCreate, ProductRead, ProductUpdate
from app.services.products import ProductService

router = APIRouter()


class ProductAPI:
    @staticmethod
    @router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
    def create_product(
        product: ProductCreate,
        db: Session = Depends(get_db),
    ):
        service = ProductService(db)
        return service.create_product(product)

    @staticmethod
    @router.get("/", response_model=list[ProductRead])
    def list_products(
        db: Session = Depends(get_db),
    ) -> list[ProductRead]:
        service = ProductService(db)
        return service.list_products()

    @staticmethod
    @router.get("/{product_id}", response_model=ProductRead)
    def get_product(
        product_id: uuid.UUID,
        db: Session = Depends(get_db),
    ) -> ProductRead:
        service = ProductService(db)
        try:
            return service.get_product(product_id)
        except NotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    @staticmethod
    @router.put("/{product_id}", response_model=ProductRead)
    def update_product(
        product_id: uuid.UUID,
        product_data: ProductUpdate,
        db: Session = Depends(get_db),
    ) -> ProductRead:
        service = ProductService(db)
        return service.update_product(product_id, product_data)

    @staticmethod
    @router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_product(
        product_id: uuid.UUID,
        db: Session = Depends(get_db),
    ):
        service = ProductService(db)
        service.delete_product(product_id)
