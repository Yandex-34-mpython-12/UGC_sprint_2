import json
import pytest
from test_data.test_kafka_message import test_kafka_message


@pytest.mark.asyncio
async def test_update_progress(
    test_client,
    mock_user,
    kafka_producer_mock
):
    response = test_client.post("/movies/update_progress", json=test_kafka_message)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json['status'] == "Message sent"
    assert response_json['message']['user_id'] == str(mock_user.uuid)
    assert response_json['message']['movie_id'] == test_kafka_message['movie_id']
    assert response_json['message']['progress'] == test_kafka_message['progress']
    assert response_json['message']['status'] == test_kafka_message['status']
    assert response_json['message']['last_watched'] == test_kafka_message['last_watched']

    kafka_producer_mock.send_and_wait.assert_called_once()
    kafka_message = json.loads(
        kafka_producer_mock.send_and_wait.call_args[0][1].decode('utf-8'))
    assert kafka_message['user_id'] == str(mock_user.uuid)
    assert kafka_message['movie_id'] == test_kafka_message['movie_id']
    assert kafka_message['progress'] == test_kafka_message['progress']
    assert kafka_message['status'] == test_kafka_message['status']
