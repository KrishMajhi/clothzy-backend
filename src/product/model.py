from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON, func

from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy.dialects import postgresql as pg


class Product(SQLModel, table=True):
    __tablename__ = "product"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )

    # =========================
    # BASIC INFO
    # =========================

    name: str = Field(index=True)

    slug: str = Field(
        unique=True,
        index=True,
    )

    description: str

    brand: Optional[str] = None

    category: str = Field(index=True)

    gender: str = Field(index=True)

    material: Optional[str] = None

    # =========================
    # PRICING
    # =========================

    price: float

    original_price: Optional[float] = None

    # =========================
    # INVENTORY
    # =========================

    stock: int = 0

    is_active: bool = True

    # =========================
    # ATTRIBUTES
    # =========================

    sizes: list[str] = Field(
        default_factory=list,
        sa_column=Column(pg.JSONB),
    )

    colors: list[str] = Field(
        default_factory=list,
        sa_column=Column(pg.JSONB),
    )

    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(pg.JSONB),
    )

    # =========================
    # IMAGES
    # =========================

    images: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )

    # =========================
    # RATINGS
    # =========================

    rating: float = 0.0

    review_count: int = 0

    # =========================
    # TIMESTAMPS
    # =========================

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now()
        )
    )
