from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.product.model import Product
from .model import Cart
from .schemas import AddToCartSchema, CartItemResponse, CartItemUpdateSchema
from src.auth.model import User
from src.product.service import ProductService

from src.errors import (
    ProductNotFoundException,
    CartItemNotFoundException,
    InvalidQuantityException,
    InsufficientStockException,
    QuantityLimitExceededException,
    InvalidColorException,
    InvalidSizeException,
    ProductAlreadyInCartException,
)

QTY_ALLOWED_PER_CUSTOMER_PER_PRODUCT = 5


class Cart_service:

    async def validated_fields(
        self, quantity: int, selectedSize: str, selectedColor: str, product
    ):
        if quantity <= 0:
            raise InvalidQuantityException()

        if quantity > product.stock:
            raise InsufficientStockException(stock=product.stock)

        if quantity > QTY_ALLOWED_PER_CUSTOMER_PER_PRODUCT:
            raise QuantityLimitExceededException(max_qty=QTY_ALLOWED_PER_CUSTOMER_PER_PRODUCT)

        if selectedColor not in product.colors:
            raise InvalidColorException()

        if selectedSize not in product.sizes:
            raise InvalidSizeException()

    async def add_Product_to_cart(
        self, addtocartData: AddToCartSchema, currentUser: User, session: AsyncSession
    ):
        product = await ProductService().get_product_by_uid(
            session=session, p_id=addtocartData.product_id
        )
        if product is None:
            raise ProductNotFoundException()

        await self.validated_fields(
            addtocartData.quantity,
            addtocartData.selected_size,
            addtocartData.selected_color,
            product,
        )

        existing_item = await self.get_cart_item_by_productID(
            addtocartData.product_id,
            addtocartData.selected_size,
            addtocartData.selected_color,
            session,
            currentUser,
        )

        if existing_item:
            raise ProductAlreadyInCartException()

        new_cart_item = Cart(**addtocartData.model_dump())
        new_cart_item.user_id = currentUser.uid
        session.add(new_cart_item)
        await session.commit()
        await session.refresh(new_cart_item)
        return new_cart_item

    async def get_cart_item_by_productID(
        self,
        product_id: str,
        selected_size: str,
        selected_color: str,
        session: AsyncSession,
        currentUser: User,
    ):
        stmt = select(Cart).where(
            Cart.product_id == product_id,
            Cart.user_id == currentUser.uid,
            Cart.selected_size == selected_size,
            Cart.selected_color == selected_color,
        )

        result = await session.exec(stmt)
        return result.first()

    async def get_allItems_in_cart(
        self,
        session: AsyncSession,
        currentUser: User,
    ):
        stmt = (
            select(Cart, Product)
            .join(Product, Cart.product_id == Product.id)
            .where(Cart.user_id == currentUser.uid)
        )

        result = await session.exec(stmt)
        rows = result.all()
        response = []

        for cart_item, product in rows:
            subtotal = product.price * cart_item.quantity
            response.append(
                CartItemResponse(
                    cart_id=cart_item.uid,
                    product_id=product.id,
                    name=product.name,
                    category=product.category,
                    gender=product.gender,
                    brand=product.brand,
                    material=product.material,
                    rating=product.rating,
                    review_count=product.review_count,
                    image=(product.images[0] if product.images else None),
                    price=product.price,
                    original_price=product.original_price,
                    stock=product.stock,
                    quantity=cart_item.quantity,
                    selected_size=cart_item.selected_size,
                    selected_color=cart_item.selected_color,
                    subtotal=subtotal,
                )
            )

        return response

    async def update_cart_item(
        self,
        cart_item_id: str,
        updatedcartdata: CartItemUpdateSchema,
        session: AsyncSession,
        currentUser: User,
    ):
        stmt = select(Cart).where(
            Cart.uid == cart_item_id, Cart.user_id == currentUser.uid
        )
        result = await session.exec(stmt)
        cart_item = result.first()

        if cart_item is None:
            raise CartItemNotFoundException()

        product = await ProductService().get_product_by_uid(
            session=session, p_id=cart_item.product_id
        )
        await self.validated_fields(
            updatedcartdata.quantity,
            cart_item.selected_size,
            cart_item.selected_color,
            product,
        )

        cart_item.quantity = updatedcartdata.quantity
        session.add(cart_item)
        await session.commit()
        await session.refresh(cart_item)
        return cart_item

    async def remove_cart_item(
        self, cart_item_id: str, session: AsyncSession, currentUser: User
    ):
        stmt = select(Cart).where(
            Cart.uid == cart_item_id, Cart.user_id == currentUser.uid
        )
        result = await session.exec(stmt)
        cart_item = result.first()

        if cart_item is None:
            raise CartItemNotFoundException()

        await session.delete(cart_item)
        await session.commit()
        return True

    async def clear_cart(self, session: AsyncSession, currentUser: User):
        stmt = select(Cart).where(Cart.user_id == currentUser.uid)
        result = await session.exec(stmt)
        cart_items = result.all()
        for item in cart_items:
            await session.delete(item)
        await session.commit()
        return {"detail": "Cart cleared successfully"}  