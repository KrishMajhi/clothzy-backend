from sqlmodel import SQLModel, Field, Column, func

from sqlalchemy.dialects import postgresql as pg
import uuid
from datetime import datetime

# uid: uuid.UUID = Field(
#     sa_column=Column(
#         pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False
#     )
# )
# uid:uuid.UUID=Field(default=pg.UUID,primary_key=True,default_factory=uuid.uuid4,nullable=False)


# table=true
class User(
    SQLModel, table=True
):  #!the table = true is neccessary for table creation .same for tablename
    __tablename__ = "user"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )

    username: str
    email: str
    email_verified: bool=Field(default=False)

    hashed_password: str = Field(nullable=False, exclude=True)
    # personal
    fullname: str | None = None
    phone_number: str | None = None
    phone_verified: bool = False
    # address
    address_line_1: str | None = None
    address_line_2: str | None = None

    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None

    role: str = Field(default="user")
    is_active: bool = Field(default=True)
    

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now()
        )
    )

    def __repr__(self) -> str:

        return f"<User(user_uid={self.uid}, username='{self.username}', email='{self.email}')>"
