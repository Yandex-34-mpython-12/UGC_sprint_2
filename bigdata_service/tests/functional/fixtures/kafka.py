from unittest.mock import patch

import pytest_asyncio
from aiohttp import ClientSession
from src.core.config import settings
from src.models import User


@pytest_asyncio.fixture
async def aiohttp_client():
    async with ClientSession() as session:
        yield session


@pytest_asyncio.fixture
def kafka_producer_mock():
    with patch('src.services.kafka.get_kafka_producer') as kafka_producer:
        yield kafka_producer


@pytest_asyncio.fixture
def mock_user():
    user = User(uuid="12345", name="Test User", email="testuser@example.com")
    with patch('src.api.auth.get_current_user_global', return_value=user):
        yield user


@pytest_asyncio.fixture
async def test_update_progress(aiohttp_client, kafka_producer_mock, mock_user):
    kafka_producer_mock.return_value.send_and_wait = patch(
        'aio_kafka_producer.send_and_wait', return_value=None)

    progress_data = {
        "movie_id": "67890",
        "progress": 45,
        "status": "watching",
        "last_watched": "2024-09-01 12:30:00"
    }

    async with aiohttp_client.post(f"{settings.api_base_url}/movies/update_progress", json=progress_data) as response:
        assert response.status == 200
        response_json = await response.json()

        assert response_json['status'] == "Message sent"
        assert response_json['message']['user_id'] == str(mock_user.uuid)
        assert response_json['message']['movie_id'] == progress_data['movie_id']
        assert response_json['message']['progress'] == progress_data['progress']
        assert response_json['message']['status'] == progress_data['status']
        assert response_json['message']['last_watched'] == progress_data['last_watched']
