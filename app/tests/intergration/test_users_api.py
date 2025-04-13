from fastapi.testclient import TestClient
from app.main import app
from app.tests.intergration.conftest import auth_header

client = TestClient(app)


def test_register_user():
    new_user = {
        "email": "test@test.com",
        "name": "Test User",
        "password": "testpassword",
    }

    response = client.post("/users/register", json=new_user)
    assert response.status_code == 201
    assert response.json()["email"] == new_user["email"]
    assert response.json()["name"] == new_user["name"]
    assert "id" in response.json()
    assert "hashed_password" not in response.json()

# test register
#   user with existing email
#   user with invalid email
#   user with invalid password ??
# test login_user
#   get login user with valid credentials
#   get login user with invalid credentials
#   get login user with non existing user
# test update user
#   get update email and name
#   get update email
#   get update name
#   get update none existing user
#   get update user with no changes
#   get update user with invalid data
# test get user
#  get user doesn't exist
#  get user exists
