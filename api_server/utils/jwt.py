import jwt
from typing import Any

from api_server.config import settings
from api_server.exceptions import InvalidTokenException


class JwtTool:

    ALG = "HS256"
    SECRET = settings.JWT_SECRET

    @classmethod
    def create_token(cls, payload: dict[str, Any]) -> str:
        return jwt.encode(
            payload=payload,
            key=cls.SECRET,
            algorithm=cls.ALG
        )

    @classmethod
    def read_token(cls, token: str) -> dict[str, Any]:
        try:
            payload: dict[str, Any] = jwt.decode(
                jwt=token,
                key=cls.SECRET,
                algorithms=[cls.ALG]
            )
            return payload
        except jwt.InvalidTokenError:
            raise InvalidTokenException()  #todo добавить обработку этого исключения
