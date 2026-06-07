import http

from fastapi.security import HTTPBearer
from fastapi import Request

from src.db.database import get_session
from .utility import decode_token

from fastapi import Depends
from .service import UserService

from src.errors import (
    InvalidTokenException,
    InvalidAccessTokenException,
    InvalidRefreshTokenException,
    UserNotFoundException,
    UnauthorizedException,
    ForbiddenException,
)


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        creds = await super().__call__(request)
        token_from_client = creds.credentials

        token_detail = self.valid_token(token_from_client)

        if token_detail is None:
            raise InvalidTokenException()

        self.verify_token(token_detail)
        return token_detail

    def valid_token(self, token: str):
        token_detail = decode_token(token)
        return token_detail if token_detail is not None else None

    def verify_token(self, token_data: dict):
        raise NotImplementedError("Subclasses must implement this method")


class Access_token_bearer(TokenBearer):
    def verify_token(self, token_data: dict):
        if token_data["refresh"]:
            raise InvalidAccessTokenException()


class Refresh_token_bearer(TokenBearer):
    def verify_token(self, token_data: dict):
        if not token_data["refresh"]:
            raise InvalidRefreshTokenException()


async def get_current_user(
    session=Depends(get_session), token_data: dict = Depends(Access_token_bearer())
):
    current_user = await UserService().get_user_by_uid(
        session, token_data["user"]["user_uid"]
    )
    if current_user is None:
        raise UserNotFoundException()

    return current_user


class Role_checker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user=Depends(get_current_user)):

        if current_user is None:
            raise UnauthorizedException()

        if current_user.role not in self.allowed_roles:
            raise ForbiddenException()

        return True