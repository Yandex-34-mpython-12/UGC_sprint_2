from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from src.utils.user_agent import DeviceType


class HistoryBase(BaseModel):
    user_id: UUID
    logged_in_at: datetime
    user_agent: str
    user_device_type: DeviceType


class HistoryRead(HistoryBase):
    id: UUID
