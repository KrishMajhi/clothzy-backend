from datetime import timedelta
from .model import User

from fastapi import APIRouter, Depends

from .utility import verify_password, create_access_token
from .schemas.usermodel import (
    change_password_model,
    user_model,
    user_create_model,
    user_login_model,
    user_update_model,
    build_user_response,
)
from .service import UserService
from src.db.database import get_session
from .dependencies import Access_token_bearer, get_current_user, Role_checker

from src.errors import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException,
    OldPasswordIncorrectException,
    SamePasswordException,
)

user_router = APIRouter()
userService = UserService()
REFRESH_TOKEN_EXPIRY_IN_DAYS = 7


@user_router.post("/signup", response_model=user_model)
async def user_register(userdata: user_create_model, session=Depends(get_session)):
    user_exits = await userService.user_exists(session, userdata.personal_info.email)
    if user_exits:
        raise UserAlreadyExistsException()

    new_user = await userService.create_user(session, userdata)
    return build_user_response(new_user)


@user_router.post("/login")
async def user_login(user_creds: user_login_model, session=Depends(get_session)):
    user = await userService.get_user_by_email(session, user_creds.email)

    if user and verify_password(user.hashed_password, user_creds.password):
        access_token = create_access_token(
            {
                "user_uid": str(user.uid),
                "username": user.username,
                "email": user.email,
            }
        )

        refresh_token = create_access_token(
            {
                "user_uid": str(user.uid),
                "username": user.username,
                "email": user.email,
            },
            refresh=True,
            expiry=timedelta(days=7),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token": "Bearer",
            "user": {
                "user_uid": str(user.uid),
                "username": user.username,
                "email": user.email,
            },
        }

    raise InvalidCredentialsException()


@user_router.get("/me")
async def current_user(current_user: User = Depends(get_current_user)):
    return build_user_response(current_user)


@user_router.get("/tokenCheck")
async def check_token(token: str = Depends(Access_token_bearer())):
    return "passed"


@user_router.patch("/update_profile", response_model=user_model)
async def update_user(
    user_updatedata: user_update_model,
    session=Depends(get_session),
    current_active_user: User = Depends(get_current_user),
):
    updated_user = await userService.update_user(
        session,
        current_active_user.uid,
        user_updatedata,
    )

    if updated_user is None:
        raise UserNotFoundException()

    return build_user_response(updated_user)


@user_router.patch("/update_password/")
async def update_password(
    password_data: change_password_model,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(current_user.hashed_password, password_data.old_password):
        raise OldPasswordIncorrectException()
    if password_data.old_password == password_data.new_password:
        raise SamePasswordException()
    await userService.change_password(session, password_data, current_user)
    return {"detail": "password updated successfully"}


@user_router.delete("/delte_account")
async def delte_account(
    password: str,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    dleted = await userService.delete_account(session, current_user.uid, password)
    if dleted is None:
        raise UserNotFoundException(detail="User not found or password is incorrect")
    return {"detail": "account deleted successfully"}