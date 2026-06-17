import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field


class Wishlist(SQLModel, table=True):
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    user_id: uuid.UUID = Field(
        foreign_key="user.uid"
    )

    product_id: uuid.UUID = Field(
        foreign_key="product.id"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
