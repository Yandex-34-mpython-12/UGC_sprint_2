import http
import json
import uuid

import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from src.tests.functional.settings import test_settings
from src.tests.functional.testdata.es_mapping import ES_PERSONS_INDEX_MAPPING


@pytest_asyncio.fixture(name='elastic_persons_index', scope='session')
def elastic_persons_index():
    return test_settings.elastic_persons_index


@pytest_asyncio.fixture(name='es_write_persons', scope='session', autouse=True)
async def es_write_persons(es_client: AsyncElasticsearch, elastic_persons_index: str):
    # Generate mock data for each person
    es_data = [
        {
            'id': str(uuid.uuid4()),
            'person': 'John Sayles',
            'films': [
                {'id': str(uuid.uuid4()), 'imdb_rating': 7.4,
                 'title': 'Lone Star', 'role': 'writer'},
                {'id': str(uuid.uuid4()), 'imdb_rating': 7.4,
                 'title': 'Lone Star', 'role': 'director'},
            ],
        },
        {
            'id': str(uuid.uuid4()),
            'person': 'Naohisa Inoue',
            'films': [
                {'id': str(uuid.uuid4()), 'title': 'The Day I Bought a Star',
                 'imdb_rating': 8, 'role': 'writer'}
            ],
        },
    ]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': elastic_persons_index, '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    if await es_client.indices.exists(index=elastic_persons_index):
        await es_client.indices.delete(index=elastic_persons_index)
    await es_client.indices.create(index=elastic_persons_index, **ES_PERSONS_INDEX_MAPPING)

    updated, errors = await async_bulk(client=es_client, actions=bulk_query, refresh='wait_for')

    if errors:
        raise Exception('Ошибка записи данных в Elasticsearch')

    yield bulk_query

    await es_client.indices.delete(index=elastic_persons_index)


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Search for all persons
        ({'page_size': 1, 'page_number': 1}, {
         'status': http.HTTPStatus.OK, 'length': 1}),
        # Search for one person by a surname
        ({'query': 'Sayles', 'page_size': 1, 'page_number': 1},
         {'status': http.HTTPStatus.OK, 'length': 1}),
    ],
)
@pytest.mark.asyncio(scope='session')
async def test_persons(make_get_request, query_data: dict, expected_answer: dict):
    # 1. Запрашиваем данные из ES по API
    response = await make_get_request('/api/v1/persons/search', query_data)
    rsp_body = response.json()

    # 2. Проверяем ответ
    assert response.status_code == expected_answer['status']
    assert len(rsp_body) == expected_answer['length']


@pytest.mark.asyncio(scope='session')
async def test_person_by_id(make_get_request, es_write_persons, redis_client):
    ok_person_id = es_write_persons[0]['_id']
    response = await make_get_request(f'/api/v1/persons/{ok_person_id}', params={})
    person = response.json()
    assert person['uuid'] == ok_person_id
    assert response.status_code == http.HTTPStatus.OK

    person_from_cache = await redis_client.get(f'person:{ok_person_id}')
    assert person_from_cache is not None

    cached_person_id = json.loads(json.loads(person_from_cache))['uuid']
    assert cached_person_id == ok_person_id

    err_person_id = uuid.uuid4()
    err_response = await make_get_request(f'/api/v1/persons/{err_person_id}', params={})
    assert err_response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio(scope='session')
async def test_persons_films(make_get_request, es_write_persons):
    # 1. Запрашиваем данные из ES по API
    ok_person_id = es_write_persons[0]['_id']
    ok_person_film_id = es_write_persons[0]['_source']['films'][0]['id']
    print(ok_person_film_id)
    ok_person_films_length = len(es_write_persons[0]['_source']['films'])
    response = await make_get_request(f'/api/v1/persons/{ok_person_id}/film', params={})
    films = response.json()

    # 2. Проверяем ответ
    assert response.status_code == http.HTTPStatus.OK
    assert films[0]['uuid'] == ok_person_film_id
    assert len(films) == ok_person_films_length
