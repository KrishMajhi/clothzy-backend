from ast import stmt

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, desc, or_

from .schema import (
    CreateOrderRequest,
    OrderDetailResponse,
    OrderItemResponse,
    OrderResponse,
)
from src.auth.model import User
from src.cart.model import Cart
from src.cart.service import Cart_service, CartItemResponse
from src.product.model import Product
from src.product.service import ProductService
from fastapi import HTTPException
from .models import Order, OrderItem, ShippingMethod

cart_service = Cart_service()

# create_order()

# 1. Get Cart Items

# 2. Lock Products

# 3. Validate Stock

# 4. Calculate Totals

# 5. Create Order

# 6. Create OrderItems

# 7. Reduce Stock

# 8. Clear Cart

# 9. Commit


class OrderService:
    async def calculate_total_amount(
        self,
        subtotal: float,
        shipping_method: ShippingMethod,
    ):
        config = await cart_service.ordersummaryConfig()

        tax = subtotal * (config["tax_percentage"] / 100)

        delivery_charge = 0

        if subtotal < config["delivery_charge_threshold"]:
            delivery_charge = config["base_delivery_charge"]

        shipping_charge = 0

        if shipping_method == ShippingMethod.EXPRESS:
            shipping_charge = config["express_shipping_charge"]

        elif shipping_method == ShippingMethod.SAME_DAY:
            shipping_charge = config["same_day_shipping_charge"]

        discount = 0

        total_amount = subtotal + tax + delivery_charge + shipping_charge - discount

        return {
            "tax": tax,
            "delivery_charge": delivery_charge,
            "shipping_charge": shipping_charge,
            "discount": discount,
            "total_amount": total_amount,
        }

    async def create_userOrder(
        self,
        neworderdata: CreateOrderRequest,
        current_user: User,
        session: AsyncSession,
    ):

        cartdata = await cart_service.get_allItems_in_cart(session, current_user)

        if not cartdata:
            raise HTTPException(status_code=400, detail="Cart is empty")
        locked_products = {}

        for item in cartdata:

            product = await session.scalar(
                select(Product).where(Product.id == item.product_id).with_for_update()
            )
            # locking product row
            if not product:
                raise HTTPException(
                    status_code=404, detail=f"Product not found: {item.name}"
                )

            locked_products[item.product_id] = product
        for item in cartdata:

            product = locked_products[item.product_id]

            if item.quantity > product.stock:
                raise HTTPException(
                    status_code=400, detail=f"{product.name} is out of stock"
                )
        if neworderdata.payment_method == "cod":
            # just keepinf it for check /here will come payment
            subtotal = sum(item.subtotal for item in cartdata)
            summary = await self.calculate_total_amount(
                subtotal=subtotal,
                shipping_method=neworderdata.shipping_method,
            )

            new_order = Order(
                user_id=current_user.uid,
                subtotal=subtotal,
                tax=summary["tax"],
                delivery_charge=summary["delivery_charge"],
                shipping_charge=summary["shipping_charge"],
                discount=summary["discount"],
                total_amount=summary["total_amount"],
                shipping_method=neworderdata.shipping_method,
                payment_method=neworderdata.payment_method,
                promo_code=neworderdata.promo_code,
                delivery_name=neworderdata.delivery_name,
                delivery_phone=neworderdata.delivery_phone,
                address_line_1=neworderdata.address_line_1,
                address_line_2=neworderdata.address_line_2,
                city=neworderdata.city,
                state=neworderdata.state,
                country=neworderdata.country,
                postal_code=neworderdata.postal_code,
            )

            session.add(new_order)

            await session.flush()
            try:

                for item in cartdata:
                    neworderitem = OrderItem(
                        order_id=new_order.id,
                        product_id=item.product_id,
                        product_name=item.name,
                        quantity=item.quantity,
                        price_at_purchase=item.price,
                        selected_color=item.selected_color,
                        selected_size=item.selected_size,
                        subtotal=item.subtotal,
                    )
                    session.add(neworderitem)

                    product = locked_products[item.product_id]

                    product.stock -= item.quantity

                    session.add(product)
                await cart_service.clear_cart_items_withoutCommit(session, current_user)
                await session.commit()
                await session.refresh(new_order)
                return new_order

            except Exception:
                await session.rollback()
                raise
        else:
            raise HTTPException(
                status_code="500", detail="othr payment mehtod will come later"
            )

    async def get_all_orders(
        self,
        currentuser: User,
        session: AsyncSession,
    ):
        stmt = (
            select(Order, OrderItem)
            .join(OrderItem, OrderItem.order_id == Order.id)
            .where(Order.user_id == currentuser.uid)
        )

        result = await session.exec(stmt)
        rows = result.all()

        orders_map = {}

        for order, item in rows:

            if order.id not in orders_map:
                orders_map[order.id] = {
                    "order": order,
                    "items": [],
                }

            orders_map[order.id]["items"].append(OrderItemResponse.model_validate(item))

        response = []

        for data in orders_map.values():

            response.append(
                OrderDetailResponse(
                    **data["order"].model_dump(),
                    items=data["items"],
                )
            )

        return response

    async def get_order_byId(
        self, userOrderid: str, session: AsyncSession, currentuser: User
    ):
        order_stmt = select(Order).where(
            Order.id == userOrderid,
            Order.user_id == currentuser.uid,
        )
        order = (await session.exec(order_stmt)).first()
        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )
        items_stmt = select(OrderItem).where(OrderItem.order_id == order.id)
        items = (await session.exec(items_stmt)).all()
        return OrderDetailResponse(
            **order.model_dump(),
            items=[OrderItemResponse.model_validate(item) for item in items],
        )

    async def get_recent_orders(
        self,
        currentuser: User,
        session: AsyncSession,
    ):
        stmt = (
            select(Order)
            .where(Order.user_id == currentuser.uid)
            .order_by(desc(Order.updated_at))
            .limit(5)
        )

        result = await session.exec(stmt)
        return result.all()
