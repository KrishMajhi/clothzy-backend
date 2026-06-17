from fastapi import APIRouter, Depends

from src.db.database import get_session
from src.auth.dependencies import get_current_user
from src.auth.model import User

from .service import WishlistService
from .schemas.wishlistschema import WishlistCreateModel

wishlist_router = APIRouter()

wishlist_service = WishlistService()


@wishlist_router.post("/add")
async def add_to_wishlist(
    wishlist_data: WishlistCreateModel,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await wishlist_service.add_to_wishlist(
        session,
        current_user.uid,
        wishlist_data.product_id,
    )


@wishlist_router.get("/")
async def get_user_wishlist(
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await wishlist_service.get_user_wishlist(
        session,
        current_user.uid,
    )


@wishlist_router.delete("/{product_id}")
async def remove_from_wishlist(
    product_id: str,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await wishlist_service.remove_from_wishlist(
        session,
        current_user.uid,
        product_id,
    )
