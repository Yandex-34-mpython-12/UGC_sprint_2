from fastapi_users import models
from fastapi_users.authentication import JWTStrategy
from fastapi_users.jwt import generate_jwt


class JWTRedisStrategy(JWTStrategy):
    async def write_token(self, user: models.UP) -> str:
        data = {
            "sub": str(user.id),
            "aud": self.token_audience,
            "role": user.role.name if user.role else "anonymous",
            "email": user.email,
            "is_active": user.is_active,
        }
        return generate_jwt(
            data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm
        )
