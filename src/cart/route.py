from fastapi import APIRouter, Depends

from src.db.database import get_session
from .service import Cart_service
from .schemas import AddToCartSchema, CartItemUpdateSchema, CartItemResponse
from src.auth.dependencies import get_current_user
from src.errors import CartItemNotFoundException

cartrouter = APIRouter()

cartService = Cart_service()


@cartrouter.post("/add")
async def add_to_cart(
    data: AddToCartSchema,
    currentUser=Depends(get_current_user),
    session=Depends(get_session),
):
    item = await cartService.add_Product_to_cart(data, currentUser, session)
    return item


@cartrouter.get("/items", response_model=list[CartItemResponse])
async def get_all_Items(
    currentUser=Depends(get_current_user),
    session=Depends(get_session),
):
    return await cartService.get_allItems_in_cart(session, currentUser)


@cartrouter.get("/{product_id}")
async def get_item_byproductId(
    product_id: str,
    selected_size: str,
    selected_color: str,
    currentUser=Depends(get_current_user),
    session=Depends(get_session),
):
    item = await cartService.get_cart_item_by_productID(
        product_id, selected_size, selected_color, session, currentUser
    )
    if item is not None:
        return item
    raise CartItemNotFoundException(detail="Item not found in cart")


@cartrouter.patch("/{cart_itemid}")
async def update_item_incart(
    cart_itemid: str,
    updatedData: CartItemUpdateSchema,
    currentUser=Depends(get_current_user),
    session=Depends(get_session),
):
    item = await cartService.update_cart_item(cart_itemid, updatedData, session, currentUser)
    return item


@cartrouter.delete("/clear")
async def clear_cart_items(
    currentUser=Depends(get_current_user), session=Depends(get_session)
):
    await cartService.clear_cart(session, currentUser)


@cartrouter.delete("/{cart_itemID}")
async def delete_item_incart(
    cart_itemID: str,
    currentUser=Depends(get_current_user),
    session=Depends(get_session),
):
    item = await cartService.remove_cart_item(cart_itemID, session, currentUser)
    if item:
        return {"detail": "Item removed"}