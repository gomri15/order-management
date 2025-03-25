import pytest
from unittest.mock import MagicMock
from app.schemas.users import UserCreate, UserLogin
from app.db.models import User
from app.services.users import UserService


@pytest.fixture
def mock_security_service():
    service = MagicMock()
    service.hash_password.return_value = "hashed_password"
    return service


def test_create_user(mock_db_session, mock_security_service):
    user_data = UserCreate(email="test@example.com", password="password123", name="Test User")
    service = UserService(mock_db_session, mock_security_service)

    result = service.create_user(user_data)

    mock_security_service.hash_password.assert_called_once_with("password123")
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

    assert isinstance(result, User)
    assert result.email == "test@example.com"
    assert result.hashed_password == "hashed_password"


def test_hash_and_verify_password(security_service):
    password = "supersecret"
    hashed = security_service.hash_password(password)
    assert hashed != password
    assert security_service.verify_password(password, hashed)


def test_create_access_token(security_service):
    data = {"sub": "user@example.com"}
    token = security_service.create_access_token(data)
    assert isinstance(token, str)
    assert token.count('.') == 2  # JWTs have 3 parts: header.payload.signature


def test_authenticate_user_user_not_found(user_service, mocker):
    mock_query = mocker.MagicMock()
    mock_filter = mocker.MagicMock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    user_service.db.query.return_value = mock_query

    login_data = UserLogin(email="test@test.com", password="a123456")
    result = user_service.authenticate_user(login_data=login_data)
    assert result is None
