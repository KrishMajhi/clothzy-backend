from ast import Return
from datetime import date, timedelta, datetime
import logging

from passlib.context import CryptContext  # for password
import jwt
from src.config import config
import uuid
from src.config import config

pwdcontext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_hash_password(password: str) -> str:
    hashed_pwd = pwdcontext.hash(password)
    return hashed_pwd


def verify_password(hash_pwd: str, password: str) -> bool:
    return pwdcontext.verify(password, hash_pwd)


def update_password(hash_pwd: str, oldPassword: str, newPassword: str):
    pwdcontext.verify_and_update


def create_access_token(
    user_data: dict, refresh: bool = False, expiry: timedelta = None
):
    payload = {}
    payload["jti"] = str(uuid.uuid4())  # uuid gives UUID object
    payload["user"] = user_data
    payload["exp"] = (
        datetime.now() + expiry
        if expiry is not None
        else datetime.now() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload["refresh"] = refresh

    access_token = jwt.encode(
        payload=payload, key=config.JWT_SECRET, algorithm=config.JWT_ALGORITHM
    )

    return access_token


def decode_token(token: str):
    try:
        decoded_token = jwt.decode(
            jwt=token, key=config.JWT_SECRET, algorithms=config.JWT_ALGORITHM
        )
        return decoded_token

    except jwt.PyJWTError as err:
        logging.exception(err)
        return None
