from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings
from src.models import gather_documents


async def init(*, client: AsyncIOMotorClient) -> None:
    await init_beanie(
        database=getattr(client, settings.mongo.mongodb_db_name),
        document_models=gather_documents(),  # type: ignore[arg-type]
    )
