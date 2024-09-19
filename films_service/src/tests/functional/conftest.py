import httpx
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from src.tests.functional.settings import test_settings


@pytest_asyncio.fixture(name='redis_client', scope='session')
async def redis_client():
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    await redis_client.flushdb()
    try:
        yield redis_client
    finally:
        await redis_client.flushdb()
        await redis_client.aclose()


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client():
    es_client = AsyncElasticsearch(
        hosts=f'{test_settings.elastic_schema}://{test_settings.elastic_host}:{test_settings.elastic_port}',
        verify_certs=False,
    )
    try:
        yield es_client
    finally:
        await es_client.close()


@pytest_asyncio.fixture(name='http_client', scope='session')
async def http_client():
    client = httpx.AsyncClient()
    try:
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture(name='make_get_request')
def make_get_request(http_client: httpx.AsyncClient):
    async def inner(path: str, params: dict[str, str]):
        url = test_settings.service_url + path
        r = await http_client.get(url, params=params)
        return r

    return inner
