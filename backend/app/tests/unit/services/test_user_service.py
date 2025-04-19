import uuid
from app.core.errors import NoChangeError
import pytest
from unittest.mock import MagicMock
from app.schemas.users import UserCreate, UserLogin, UserUpdate
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

def test_update_user(user_service, mocker):
    user_id = uuid.uuid4()
    update_data = UserUpdate(name="Updated Name", email="test@test.com")
    mock_user = mocker.MagicMock()
    mock_user.id = user_id
    mock_user.name = "Old Name"
    mock_user.email = "old@email.com"

    mock_query = mocker.MagicMock()
    mock_filter = mocker.MagicMock()
    mock_filter.first.return_value = mock_user
    mock_query.filter.return_value = mock_filter
    user_service.db.query.return_value = mock_query

    user_service.update_user(user_id, update_data)
    updated_user = user_service.get_user(user_id)
    assert updated_user.name == "Updated Name"
    assert updated_user.email == "test@test.com"
    
def test_update_user_single_field(user_service, mocker):
    user_id = uuid.uuid4()
    update_data = UserUpdate(name="Old Name", email="old@email.com")
    mock_user = mocker.MagicMock()
    mock_user.id = user_id
    mock_user.name = "Old Name"
    mock_user.email = "old@email.com"

    mock_query = mocker.MagicMock()
    mock_filter = mocker.MagicMock()
    mock_filter.first.return_value = mock_user
    mock_query.filter.return_value = mock_filter
    user_service.db.query.return_value = mock_query

    with pytest.raises(NoChangeError):
        user_service.update_user(user_id, update_data)
    
@pytest.mark.parametrize("user_update, to_update, not_to_update", [
    (UserUpdate(email="updated@email.com"),"email", "name"),
    (UserUpdate(name="Updated Name"), "name", "email"),
])
def test_update_user_single_field(user_service, mocker, user_update, to_update, not_to_update):
    user_id = uuid.uuid4()
    mock_user = mocker.MagicMock()
    mock_user.id = user_id
    mock_user.name = "Old Name"
    mock_user.email = "old@email.com"

    mock_query = mocker.MagicMock()
    mock_filter = mocker.MagicMock()
    mock_filter.first.return_value = mock_user
    mock_query.filter.return_value = mock_filter
    user_service.db.query.return_value = mock_query

    user_service.update_user(user_id, user_update)
    updated_user = user_service.get_user(user_id)
    assert getattr(updated_user, to_update) == getattr(user_update, to_update)
    assert getattr(updated_user, not_to_update) == getattr(mock_user, not_to_update)
    
    