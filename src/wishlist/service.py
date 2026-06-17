from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .model import Wishlist

from src.product.model import Product
class WishlistService:

    async def get_wishlist_item(
        self,
        session: AsyncSession,
        user_id,
        product_id,
    ):
        stmt = select(Wishlist).where(
            Wishlist.user_id == user_id,
            Wishlist.product_id == product_id,
        )

        result = await session.exec(stmt)
        return result.first()

    async def add_to_wishlist(
        self,
        session: AsyncSession,
        user_id,
        product_id,
    ):
        existing_item = await self.get_wishlist_item(
            session,
            user_id,
            product_id,
        )

        if existing_item:
            return existing_item

        wishlist_item = Wishlist(
            user_id=user_id,
            product_id=product_id,
        )

        session.add(wishlist_item)

        await session.commit()
        await session.refresh(wishlist_item)

        return wishlist_item

    async def get_user_wishlist(
        self,
        session,
        user_id,
    ):
        stmt = (
            select(Wishlist, Product)
            .join(Product, Wishlist.product_id == Product.id)
            .where(Wishlist.user_id == user_id)
        )

        result = await session.exec(stmt)

        rows = result.all()

        wishlist_items = []

        for wishlist, product in rows:

            discount_percentage = None

            if product.original_price and product.original_price > product.price:
                discount_percentage = round(
                    ((product.original_price - product.price) / product.original_price)
                    * 100
                )

            wishlist_items.append(
                {
                    "wishlist_id": wishlist.uid,
                    "product_id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "price": product.price,
                    "original_price": product.original_price,
                    "rating": product.rating,
                    "review_count": product.review_count,
                    "image_url": (product.images[0] if product.images else None),
                    "colors": [color for color in product.colors],
                    "discount_percentage": discount_percentage,
                }
            )

        return wishlist_items

    async def remove_from_wishlist(
        self,
        session: AsyncSession,
        user_id,
        product_id,
    ):
        wishlist_item = await self.get_wishlist_item(
            session,
            user_id,
            product_id,
        )

        if wishlist_item is None:
            return None

        await session.delete(wishlist_item)
        await session.commit()

        return True
