from pydantic import BaseModel, EmailStr, Field, field_validator
import uuid

from datetime import datetime

import re

class PersonalInfoModel(BaseModel):
    uid: uuid.UUID | None = None

    username: str | None = None
    fullname: str | None = None

    email: EmailStr | None = None
    phone_number: str | None = None
    hashed_password: str = Field(exclude=True)

    role: str | None = None
    is_active: bool | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value):
        if value and not re.fullmatch(r"^\+?[0-9]{10,15}$", value):
            raise ValueError("Invalid phone number")
        return value
class PersonalInfoCreateModel(BaseModel):
    # uid: uuid.UUID | None = None

    username: str | None = None
    fullname: str | None = None

    email: EmailStr | None = None
    phone_number: str | None = None
    # hashed_password: str = Field(exclude=True)

    role: str | None = None
    is_active: bool | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value):
        if value and not re.fullmatch(r"^\+?[0-9]{10,15}$", value):
            raise ValueError("Invalid phone number")
        return value




class PersonalInfoUpdateModel(BaseModel):
    fullname: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None