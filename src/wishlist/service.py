from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .model import Wishlist


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
        session: AsyncSession,
        user_id,
    ):
        stmt = select(Wishlist).where(
            Wishlist.user_id == user_id
        )

        result = await session.exec(stmt)
        return result.all()

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
