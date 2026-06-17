from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class WishlistCreateModel(BaseModel):
    product_id: UUID


class WishlistResponseModel(BaseModel):
    uid: UUID
    user_id: UUID
    product_id: UUID
    created_at: datetime







class WishlistItemResponse(BaseModel):
    wishlist_id: UUID
    product_id: UUID

    name: str
    category: str

    price: float
    original_price: float | None

    rating: float
    review_count: int

    image_url: str | None

    colors: list[str] = []

    discount_percentage: int | None = None