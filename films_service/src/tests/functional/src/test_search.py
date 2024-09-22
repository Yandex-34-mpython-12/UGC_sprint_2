import pytest
import http


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': 'The Star', 'page_size': 50, 'page_number': 1, 'sort': 'imdb_rating'},
            {'status': http.HTTPStatus.OK, 'length': 50},
        ),
        (
            {'query': 'The Star', 'page_size': 30, 'page_number': 1, 'sort': '-imdb_rating'},
            {'status': http.HTTPStatus.OK, 'length': 30},
        ),
        ({'query': 'Mashed potato', 'page_size': 20, 'page_number': 1},
         {'status': http.HTTPStatus.OK, 'length': 0}),
    ],
)
@pytest.mark.asyncio(scope='session')
async def test_search(make_get_request, query_data: dict, expected_answer: dict):
    # 1. Запрашиваем данные из ES по API
    response = await make_get_request('/api/v1/films/search', query_data)
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
