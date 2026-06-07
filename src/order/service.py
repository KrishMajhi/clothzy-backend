from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, desc, or_
from .schema import CreateOrderRequest
from src.auth.model import User
from src.cart.model import Cart
from src.cart.service import Cart_service, CartItemResponse
from src.product.model import Product
from src.product.service import ProductService

cart_service = Cart_service()


class OrderService:
    async def calculateData():
        pass

    async def create_userOrder(
        self, neworder: CreateOrderRequest, current_user: User, session: AsyncSession
    ):
        cartdata = list[
            CartItemResponse(
                (await cart_service.get_allItems_in_cart(session, current_user))
            )
        ]
        product=None
        for item in cartdata:
            product=select(Product).where(Product.id==item.product_id).with_for_update()

        # for item in cartdata:
        #     if item.quantity < product.qty