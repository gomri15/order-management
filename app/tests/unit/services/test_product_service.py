import pytest
from app.core.errors import NotFoundError
from app.db.models import Product
from app.schemas.products import ProductCreate
from app.services.products import ProductService


def product_service(mock_db_session):
    return ProductService(db=mock_db_session)


def test_create_product(mock_db_session):
    product_data = ProductCreate(name="Test Product",
                                 price=100.0,
                                 description="A test product",
                                 inventory_count=10,
                                 sku="TEST123")
    service = ProductService(mock_db_session)
    product = service.create_product(product_data=product_data)

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

    assert isinstance(product, Product)
    assert product.name == product_data.name
    assert product.price == product_data.price
    assert product.description == product_data.description
    assert product.inventory_count == product_data.inventory_count
    assert product.sku == product_data.sku


def test_get_product(mock_db_session):
    product_id = "123e4567-e89b-12d3-a456-426614174000"
    product = Product(id=product_id, name="Test Product", price=100.0,
                      description="A test product", inventory_count=10, sku="TEST123")
    mock_db_session.query.return_value.filter.return_value.first.return_value = product

    service = ProductService(mock_db_session)
    result = service.get_product(product_id=product_id)

    mock_db_session.query.assert_called_once_with(Product)
    mock_db_session.query.return_value.filter.assert_called_once()
    assert result == product


def test_update_product(mock_db_session):
    product_id = "123e4567-e89b-12d3-a456-426614174000"
    product = Product(id=product_id, name="Test Product", price=100.0,
                      description="A test product", inventory_count=10, sku="TEST123")
    mock_db_session.query.return_value.filter.return_value.first.return_value = product

    updates = ProductCreate(name="Updated Product", price=150.0, description="Updated description",
                            inventory_count=20, sku="UPDATED123")

    service = ProductService(mock_db_session)
    updated_product = service.update_product(product_id=product_id, updates=updates)

    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

    assert updated_product.name == updates.name
    assert updated_product.price == updates.price
    assert updated_product.description == updates.description
    assert updated_product.inventory_count == updates.inventory_count
    assert updated_product.sku == updates.sku


def test_delete_product(mock_db_session):
    product_id = "123e4567-e89b-12d3-a456-426614174000"
    product = Product(id=product_id, name="Test Product", price=100.0,
                      description="A test product", inventory_count=10, sku="TEST123")
    mock_db_session.query.return_value.filter.return_value.first.return_value = product

    service = ProductService(mock_db_session)
    service.delete_product(product_id=product_id)

    mock_db_session.delete.assert_called_once_with(product)
    mock_db_session.commit.assert_called_once()


def test_list_products(mock_db_session):
    product1 = Product(id="123e4567-e89b-12d3-a456-426614174000", name="Test Product 1", price=100.0,
                       description="A test product", inventory_count=10, sku="TEST123")
    product2 = Product(id="123e4567-e89b-12d3-a456-426614174001", name="Test Product 2", price=200.0,
                       description="Another test product", inventory_count=20, sku="TEST124")
    mock_db_session.query.return_value.all.return_value = [product1, product2]

    service = ProductService(mock_db_session)
    products = service.list_products()

    mock_db_session.query.assert_called_once_with(Product)
    assert len(products) == 2
    assert products[0] == product1
    assert products[1] == product2


def test_product_not_found(mock_db_session):
    product_id = "123e4567-e89b-12d3-a456-426614174000"
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    service = ProductService(mock_db_session)
    with pytest.raises(NotFoundError) as e:
        service.get_product(product_id=product_id)

    assert str(e.value) == f"Product with id {product_id} not found."
