import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.tests.intergration.conftest import auth_header

client = TestClient(app)


def test_create_and_get_product(test_user):
    product_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 12.99,
        "sku": "TEST-SKU2",
        "inventory_count": 100
    }
    response = client.post("/products/",
                           json=product_data,
                           headers=auth_header(str(test_user.id)))
    assert response.status_code == 201
    created_product = response.json()
    assert created_product["name"] == product_data["name"]

    product_id = created_product["id"]
    get_response = client.get(f"/products/{product_id}",
                              headers=auth_header(str(test_user.id)))
    assert get_response.status_code == 200
    assert get_response.json()["sku"] == "TEST-SKU2"


def test_get_product_not_found(test_user):
    response = client.get(f"/products/{uuid.uuid4()}",
                          headers=auth_header(str(test_user.id)))
    assert response.status_code == 404
    assert response.json()["detail"].startswith("Product not found")


def test_update_product(test_user):
    product_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 12.99,
        "sku": "TEST-SKU3",
        "inventory_count": 100
    }

    response = client.post("/products/",
                           json=product_data,
                           headers=auth_header(str(test_user.id)))

    update_product_data = {
        "name": "Updated Product",
        "description": "An updated test product",
        "price": 15.99,
        "sku": "UPDATED-SKU",
        "inventory_count": 200
    }

    client.put(f"/products/{response.json()['id']}/",
               json=update_product_data,
               headers=auth_header(str(test_user.id)))

    updated_product = client.get(f"/products/{response.json()['id']}",
                                 headers=auth_header(str(test_user.id)))

    assert updated_product.status_code == 200
    assert updated_product.json()["name"] == update_product_data["name"]
    assert updated_product.json()["description"] == update_product_data["description"]
    assert updated_product.json()["price"] == update_product_data["price"]
    assert updated_product.json()["sku"] == update_product_data["sku"]
    assert updated_product.json()["inventory_count"] == update_product_data["inventory_count"]
