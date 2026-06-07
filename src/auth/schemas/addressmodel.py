from pydantic import BaseModel, EmailStr,Field,field_validator
import uuid

from datetime import datetime
import re


class AddressModel(BaseModel):
    address_line_1: str | None = None
    address_line_2: str | None = None

    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None

    @field_validator("postal_code")
    @classmethod
    def validate_pincode(cls, value):
        if value and not re.fullmatch(r"^\d{6}$", value):
            raise ValueError("Invalid pincode")
        return value
    
class AddressUpdateModel(BaseModel):
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pincode: str | None = None