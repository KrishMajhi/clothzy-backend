import uuid

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# from src.db.database import get_session
from .utility import verify_password, generate_hash_password
from .schemas.usermodel import (
    change_password_model,
    user_create_model,
    user_model,
    user_update_model,
)
from .model import User


# user=User()
class UserService:
    async def create_user(self, session: AsyncSession, user_data: user_create_model):
        user_dict = user_data.model_dump(exclude={"password"})
        flat_data = {}
        for section, section_data in user_dict.items():
            if isinstance(section_data, dict):
                flat_data.update(section_data)

        new_user = User(**flat_data)
        new_user.hashed_password = generate_hash_password(user_data.password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    async def get_user_by_email(self, session: AsyncSession, user_email: str):
        stmt = select(User).where(User.email == user_email)
        result = await session.exec(statement=stmt)
        return result.first()

    async def get_user_by_uid(self, session: AsyncSession, user_uid: str):
        stmt = select(User).where(User.uid == user_uid)
        result = await session.exec(statement=stmt)
        return result.first()

    async def user_exists(self, session: AsyncSession, user_email: str):
        user_from_email = await self.get_user_by_email(session, user_email)
        return True if user_from_email is not None else False

    async def update_user(
        self,
        session: AsyncSession,
        user_uid: str,
        user_data_updates: user_update_model,
    ):
        existed_user = await self.get_user_by_uid(
            session, user_uid
        )  # it gives user object

        if existed_user is not None:
            updated_data = user_data_updates.model_dump(exclude_unset=True)

            for section, section_data in updated_data.items():

                if isinstance(section_data, dict):

                    for field, field_data in section_data.items():

                        if hasattr(existed_user, field):
                            setattr(existed_user, field, field_data)

                else:

                    if hasattr(existed_user, section):
                        setattr(existed_user, section, section_data)

            await session.commit()
            await session.refresh(existed_user)
            return existed_user
        return None

    async def change_password(
        self,
        session: AsyncSession,
        password_data: change_password_model,
        current_user: User,
    ):
        # dont have to give email to chekc as its coming getting chekced with token in current user so wont repeat
        # just gonna use serivce for db relatd stuff,so rouete is where ill check condiotions and pass proper arguments
        current_user.hashed_password = generate_hash_password(
            password_data.new_password
        )
        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

    async def delete_account(
        self,
        password: str,
        session: AsyncSession,
        user_uid: str,
    ):
        user_to_delete = await self.get_user_by_uid(
            session,
            user_uid,
        )

        if user_to_delete is not None and verify_password(
            user_to_delete.hashed_password,
            password,
        ):

            await session.delete(user_to_delete)
            await session.commit()
            return True

        return None
