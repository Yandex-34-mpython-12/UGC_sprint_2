from aiochclient import ChClient
from aiohttp import ClientSession


class ClickhouseService:
    def __init__(self, client: ChClient):
        self.client = client

    async def batch_insert(self, data: list[tuple]):
        await self.client.execute(
            """
            INSERT INTO user_movie_progress
            (user_id, movie_id, progress, status, last_watched)
            VALUES
            """,
            *data
        )

    async def create_table(self):
        await self.client.execute(
            """
            CREATE TABLE IF NOT EXISTS user_movie_progress (
                user_id UUID,
                movie_id UUID,
                progress Float32,
                status Enum8('in_progress' = 1, 'completed' = 2),
                last_watched DateTime
            ) ENGINE = ReplacingMergeTree(last_watched)
            PRIMARY KEY (user_id, movie_id);
        """
        )


def get_ch_service(session: ClientSession, url: str) -> ClickhouseService:
    ch_client = ChClient(session, url=url)
    return ClickhouseService(ch_client)
