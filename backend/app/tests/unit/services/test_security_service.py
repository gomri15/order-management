
import pytest
from app.core.errors import TokenDecodeError


def test_invalid_jwt_token(security_service):
    token = "invalid_token"
    with pytest.raises(TokenDecodeError):
        security_service.decode_access_token(token)
