from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Annotated, Optional
import re
import uuid
from datetime import datetime
from src.auth.model import User

from .addressmodel import AddressModel, AddressUpdateModel
from .personalinfo import PersonalInfoCreateModel, PersonalInfoModel, PersonalInfoUpdateModel


class user_create_model(BaseModel):

    personal_info: PersonalInfoCreateModel

    password: Annotated[
        str,
        Field(min_length=8, max_length=72, exclude=True),
    ]

    address: AddressModel | None = None
    #

    @field_validator("password")
    @classmethod
    def validating_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value


class user_model(BaseModel):
    personal_info: PersonalInfoModel
    address: AddressModel | None = None


class user_login_model(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(exclude=True)


class user_update_model(BaseModel):
    personal_info: PersonalInfoUpdateModel | None = None
    address: AddressUpdateModel | None = None


class change_password_model(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validating_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value


# def build_user_response(user: User):
#     response_data = {}
#     for section_name, field_info in user_model.model_fields.items():

#         section_model = field_info.annotation

#         response_data[section_name] = section_model.model_validate(
#             user, from_attributes=True
#         )

#     return user_model(**response_data)




def build_user_response(user: User):
    return user_model(
        personal_info=PersonalInfoModel.model_validate(
            user,
            from_attributes=True,
        ),
        address=AddressModel.model_validate(
            user,
            from_attributes=True,
        ),
    )