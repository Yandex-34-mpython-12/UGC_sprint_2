import asyncio
import logging

from aiohttp import ClientSession
from core.config import settings
from services.clickhouse import ClickhouseService, get_ch_service
from services.kafka import consume
from services.transformer import prepare_data

logger = logging.getLogger(__name__)


async def main():
    session: ClientSession = ClientSession()
    ch_svc: ClickhouseService = get_ch_service(session, settings.ch.url)
    await ch_svc.create_table()
    try:
        logger.info("*** ETL ready to comsume ***")
        async for msgs in consume():
            data = prepare_data(msgs)
            if data:
                await ch_svc.batch_insert(data)
                logger.info(
                    f"Successfully inserted {len(data)} messages into db"
                )
    finally:
        await session.close()
        logger.info("*** Bye ***")


if __name__ == "__main__":
    asyncio.run(main())
