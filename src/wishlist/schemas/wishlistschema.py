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
