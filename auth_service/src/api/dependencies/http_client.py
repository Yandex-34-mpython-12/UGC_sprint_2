import httpx


async def get_http_client():
    client = httpx.AsyncClient()
    try:
        yield client
    finally:
        await client.aclose()
