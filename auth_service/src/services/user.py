from uuid import UUID

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from src.models import UserSignIn
from src.utils.user_agent import DeviceType


class UserService(SQLAlchemyUserDatabase):
    async def create_sign_in_history(self, user_id: UUID, user_agent: str, user_device_type: DeviceType) -> UserSignIn:
        user_sign_in = UserSignIn(
            user_id=user_id,
            user_agent=user_agent,
            user_device_type=user_device_type.value
        )
        self.session.add(user_sign_in)
        await self.session.commit()
        await self.session.refresh(user_sign_in)
        return user_sign_in
