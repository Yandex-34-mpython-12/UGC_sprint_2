import http
import json
import random
import uuid

import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from src.tests.functional.settings import test_settings
from src.tests.functional.testdata.es_mapping import ES_MOVIES_INDEX_MAPPING


@pytest_asyncio.fixture(name='elastic_films_index', scope='session')
def elastic_films_index():
    return test_settings.elastic_films_index


@pytest_asyncio.fixture(name='es_write_films', scope='session', autouse=True)
async def es_write_films(es_client: AsyncElasticsearch, elastic_films_index: str):
    es_data = [
        {
            'id': str(uuid.uuid4()),
            'imdb_rating': round(random.uniform(1, 9), 1),
            'genres': [{'id': str(uuid.uuid4()), 'name': 'Action'}, {'id': str(uuid.uuid4()), 'name': 'Sci-Fi'}],
            'title': 'The Star',
            'description': 'New World',
            'directors_names': ['Stan'],
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'directors': [
                {'id': 'ed86b9ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Shon'},
                {'id': 'fb123f22-121e-44a7-b78f-b19191810fbf', 'name': 'Mon'},
            ],
            'actors': [
                {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
                {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'},
            ],
            'writers': [
                {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
                {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'},
            ],
        }
        for _ in range(50)
    ]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': elastic_films_index, '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    if await es_client.indices.exists(index=elastic_films_index):
        await es_client.indices.delete(index=elastic_films_index)
    await es_client.indices.create(index=elastic_films_index, **ES_MOVIES_INDEX_MAPPING)

    updated, errors = await async_bulk(client=es_client, actions=bulk_query, refresh='wait_for')

    if errors:
        raise Exception('Ошибка записи данных в Elasticsearch')

    yield bulk_query

    await es_client.indices.delete(index=elastic_films_index)


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        ({'page_size': 50, 'page_number': 1, 'sort': 'imdb_rating'},
         {'status': http.HTTPStatus.OK, 'length': 50}),
        ({'page_size': 30, 'page_number': 1, 'sort': '-imdb_rating'},
         {'status': http.HTTPStatus.OK, 'length': 30}),
    ],
)
@pytest.mark.asyncio(scope='session')
async def test_films(make_get_request, query_data: dict, expected_answer: dict):
    # 1. Запрашиваем данные из ES по API
    response = await make_get_request('/api/v1/films/', query_data)
    rsp_body = response.json()

    if len(rsp_body) > 1 and query_data.get('sort'):
        sort = query_data.get('sort')
        if sort.startswith('-'):
            assert rsp_body[0]['imdb_rating'] > rsp_body[-1]['imdb_rating']
        else:
            assert rsp_body[0]['imdb_rating'] < rsp_body[-1]['imdb_rating']

    # 3. Проверяем ответ
    assert response.status_code == expected_answer['status']
    assert len(rsp_body) == expected_answer['length']


@pytest.mark.asyncio(scope='session')
async def test_film_by_id(
    make_get_request,
    es_write_films,
    redis_client,
):
    ok_film_id = es_write_films[0]['_id']
    response = await make_get_request(f'/api/v1/films/{ok_film_id}', params={})
    film = response.json()
    assert film['uuid'] == ok_film_id
    assert response.status_code == http.HTTPStatus.OK

    film_from_cache = await redis_client.get(f'film:{ok_film_id}')
    assert film_from_cache is not None

    print(json.loads(film_from_cache))
    cached_film_id = json.loads(json.loads(film_from_cache))['uuid']
    assert cached_film_id == ok_film_id

    err_film_id = uuid.uuid4()
    err_response = await make_get_request(f'/api/v1/films/{err_film_id}', params={})
    assert err_response.status_code == http.HTTPStatus.NOT_FOUND
