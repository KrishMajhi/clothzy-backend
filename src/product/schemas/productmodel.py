from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class ProductSort(str, Enum):
    newest = "newest"
    oldest = "oldest"
    price_low_to_high = "price_low_to_high"
    price_high_to_low = "price_high_to_low"
    rating = "rating"


class Gender(str, Enum):
    men = "men"
    women = "women"
    kids = "kids"
    unisex = "unisex"


class ProductCategory(str, Enum):
    tshirt = "tshirt"
    shirt = "shirt"
    hoodie = "hoodie"
    jacket = "jacket"
    jeans = "jeans"
    shorts = "shorts"
    kurta = "kurta"


class ProductCreateModel(BaseModel):

    name: str

    slug: str

    description: str

    brand: Optional[str] = None

    category: ProductCategory

    gender: Gender

    material: Optional[str] = None

    price: float = Field(gt=0)

    original_price: Optional[float] = Field(
        default=None,
        gt=0,
    )

    stock: int = Field(
        default=0,
        ge=0,
    )

    sizes: list[str]

    colors: list[str]

    tags: list[str] = Field(default_factory=list)

    images: list[str]

    is_active: bool = True


class ProductUpdateModel(BaseModel):

    name: Optional[str] = None

    slug: Optional[str] = None

    description: Optional[str] = None

    brand: Optional[str] = None

    category: Optional[ProductCategory] = None

    gender: Optional[Gender] = None

    material: Optional[str] = None

    price: Optional[float] = Field(
        default=None,
        gt=0,
    )

    original_price: Optional[float] = Field(
        default=None,
        gt=0,
    )

    stock: Optional[int] = Field(
        default=None,
        ge=0,
    )

    sizes: Optional[list[str]] = None

    colors: Optional[list[str]] = None

    tags: Optional[list[str]] = None

    images: Optional[list[str]] = None

    is_active: Optional[bool] = None


class ProductResponseModel(BaseModel):

    id: uuid.UUID

    name: str

    slug: str

    description: str

    brand: Optional[str]

    category: ProductCategory

    gender: Gender

    material: Optional[str]

    price: float

    original_price: Optional[float]

    stock: int

    sizes: list[str]

    colors: list[str]

    tags: list[str]

    images: list[str]

    rating: float

    review_count: int

    is_active: bool

    created_at: datetime

    updated_at: datetime


class ProductListResponseModel(BaseModel):
    items: list[ProductResponseModel]

    total: int

    page: int

    limit: int

    total_pages: int