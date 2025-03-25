from fastapi import HTTPException
import jwt
import pytest

from app.auth.dependencies import get_current_user
from app.core.errors import TokenDecodeError


def test_no_user_id_in_token(security_service, mocker):
    mock_decode = mocker.MagicMock()
    mock_decode.return_value = {"sub": None}
    security_service.decode_access_token = mock_decode

    token = "invalid_token"
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(token=token, db=None, security_service=security_service)

    assert excinfo.value.status_code == 401
    assert str(excinfo.value.detail) == "Invalid token"


def test_user_not_found(security_service, mocker):
    mock_decode = mocker.MagicMock()
    mock_decode.return_value = {"sub": "user_id"}
    security_service.decode_access_token = mock_decode

    mock_query = mocker.MagicMock()
    mock_query.filter.return_value.first.return_value = None
    db_mock = mocker.MagicMock()
    db_mock.query.return_value = mock_query

    token = "valid_token"
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(token=token, db=db_mock, security_service=security_service)

    assert excinfo.value.status_code == 401
    assert str(excinfo.value.detail) == "User not found"


def test_successful_user_retrieval(security_service, mocker):
    mock_decode = mocker.MagicMock()
    mock_decode.return_value = {"sub": "user_id"}
    security_service.decode_access_token = mock_decode

    mock_user = mocker.MagicMock()
    mock_query = mocker.MagicMock()
    mock_query.filter.return_value.first.return_value = mock_user
    db_mock = mocker.MagicMock()
    db_mock.query.return_value = mock_query

    token = "valid_token"
    user = get_current_user(token=token, db=db_mock, security_service=security_service)

    assert user == mock_user
