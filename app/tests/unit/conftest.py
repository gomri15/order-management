
from unittest.mock import MagicMock

import pytest

from app.core.security import SecurityService
from app.services.users import UserService


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    return session


@pytest.fixture
def user_service(mock_db_session, security_service):
    return UserService(db=mock_db_session, security_service=security_service)


@pytest.fixture
def security_service():
    return SecurityService()
