from typing import Optional
import uuid

from pydantic import BaseModel, Field


class AddToCartSchema(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(gt=0, default=1)
    selected_size: str | None = None

    selected_color: str | None = None


class CartItemUpdateSchema(BaseModel):

    quantity: int = Field(gt=0, default=1)


# class AddToCartResponseSchema(BaseModel):

#   "user_id": "3acc561d-7b6f-4c69-a907-ed943ff41686",
#   "uid": "afa2940c-dcb6-4d82-8f67-47c44fc460c7",
#   product_id: uuid.UUID
#   quantity: int


class CartItemResponse(BaseModel):
    cart_id: uuid.UUID
    product_id: uuid.UUID

    name: str

    category: str
    gender: str

    brand: Optional[str] = None
    material: Optional[str] = None

    rating: float
    review_count: int

    image: Optional[str] = None

    price: float
    original_price: Optional[float] = None

    stock: int

    quantity: int

    selected_size: str
    selected_color: str
    subtotal:float