import pytest
from aiohttp import ClientSession
from src.main import app

@pytest.fixture
def test_client():
    client = ClientSession(app)
    yield client
