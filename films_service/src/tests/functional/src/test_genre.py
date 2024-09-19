import json
import uuid
import http
import pytest
import pytest_asyncio

from elasticsearch.helpers import async_bulk
from elasticsearch import AsyncElasticsearch
from src.tests.functional.testdata.es_mapping import ES_GENRES_INDEX_MAPPING
from src.tests.functional.settings import test_settings


@pytest_asyncio.fixture(name='elastic_genres_index', scope='session')
def elastic_genres_index():
    return test_settings.elastic_genres_index


@pytest_asyncio.fixture(name='es_write_genres', scope='session', autouse=True)
async def es_write_genres(es_client: AsyncElasticsearch, elastic_genres_index: str):
    # List of genres with their UUIDs
    genres = [
        {'uuid': '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff', 'name': 'Action'},
        {'uuid': '120a21cf-9097-479e-904a-13dd7198c1dd', 'name': 'Adventure'},
        {'uuid': '6a0a479b-cfec-41ac-b520-41b2b007b611', 'name': 'Animation'},
        {'uuid': 'ca124c76-9760-4406-bfa0-409b1e38d200', 'name': 'Biography'},
        {'uuid': '5373d043-3f41-4ea8-9947-4b746c601bbd', 'name': 'Comedy'},
        {'uuid': '63c24835-34d3-4279-8d81-3c5f4ddb0cdc', 'name': 'Crime'},
        {'uuid': '6d141ad2-d407-4252-bda4-95590aaf062a', 'name': 'Documentary'},
        {'uuid': '1cacff68-643e-4ddd-8f57-84b62538081a', 'name': 'Drama'},
        {'uuid': '55c723c1-6d90-4a04-a44b-e9792040251a', 'name': 'Family'},
        {'uuid': 'b92ef010-5e4c-4fd0-99d6-41b6456272cd', 'name': 'Fantasy'},
    ]

    # Generate mock data for each genre
    es_data = [{'id': str(uuid.uuid4()), 'genre': genre['name']}
               for genre in genres]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': elastic_genres_index, '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    if await es_client.indices.exists(index=elastic_genres_index):
        await es_client.indices.delete(index=elastic_genres_index)
    await es_client.indices.create(index=elastic_genres_index, **ES_GENRES_INDEX_MAPPING)

    updated, errors = await async_bulk(client=es_client, actions=bulk_query, refresh='wait_for')

    if errors:
        raise Exception('Ошибка записи данных в Elasticsearch')

    yield bulk_query

    await es_client.indices.delete(index=elastic_genres_index)


@pytest.mark.parametrize(
    'query_data, expected_answer', [({'page_size': 10, 'page_number': 1}, {
                                     'status': http.HTTPStatus.OK, 'length': 10})]
)
@pytest.mark.asyncio(scope='session')
async def test_genres(make_get_request, query_data: dict, expected_answer: dict):
    # 1. Запрашиваем данные из ES по API
    response = await make_get_request('/api/v1/genres/', query_data)
    rsp_body = response.json()

    # 2. Проверяем ответ
    assert response.status_code == expected_answer['status']
    assert len(rsp_body) == expected_answer['length']


@pytest.mark.asyncio(scope='session')
async def test_genre_by_id(make_get_request, es_write_genres, redis_client):
    ok_genre_id = es_write_genres[0]['_id']
    response = await make_get_request(f'/api/v1/genres/{ok_genre_id}', params={})
    genre = response.json()
    assert genre['uuid'] == ok_genre_id
    assert response.status_code == http.HTTPStatus.OK

    genre_from_cache = await redis_client.get(f'genre:{ok_genre_id}')
    assert genre_from_cache is not None

    cached_genre_id = json.loads(json.loads(genre_from_cache))['uuid']
    assert cached_genre_id == ok_genre_id

    err_genre_id = uuid.uuid4()
    err_response = await make_get_request(f'/api/v1/genres/{err_genre_id}', params={})
    assert err_response.status_code == http.HTTPStatus.NOT_FOUND
