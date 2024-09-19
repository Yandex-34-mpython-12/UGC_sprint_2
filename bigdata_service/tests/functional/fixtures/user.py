import pytest
from src.models import User
from unittest.mock import patch
from src.api.auth import get_current_user_global


@pytest.fixture
def mock_user():
    user = User(uuid="12345", name="Test User", email="testuser@example.com")
    with patch('src.api.auth.get_current_user_global', return_value=user):
        yield user
