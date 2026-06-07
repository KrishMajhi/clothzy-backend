from typing import Optional
import uuid

from sqlmodel import SQLModel, Field, Column

from sqlalchemy.dialects import postgresql as pg
from src.auth.model import User
from src.product.model import Product


class Cart(SQLModel, table=True):
    __tablename__ = "cart"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, default=uuid.uuid4, primary_key=True, nullable=False)
    )
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.uid")
    product_id: Optional[uuid.UUID] = Field(default=None, foreign_key="product.id")
    quantity: int = 1

    selected_size: str | None = None

    selected_color: str | None = None
