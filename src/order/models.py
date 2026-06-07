from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, func

from sqlalchemy.dialects import postgresql as pg


class ShippingMethod(str, Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    SAME_DAY = "same_day"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUND_REQUESTED = "refund_requested"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    COD = "cod"
    UPI = "upi"
    CARD = "card"
    NETBANKING = "netbanking"
    WALLET = "wallet"


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_id: UUID = Field(foreign_key="user.uid", index=True)

    subtotal: Decimal = Field(max_digits=10, decimal_places=2)

    shipping_charge: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    shipping_method: ShippingMethod
    promo_code: Optional[str] = None
    tax: int
    discount: Decimal = Field(default=0, max_digits=10, decimal_places=2)

    total_amount: Decimal = Field(max_digits=10, decimal_places=2)

    payment_status: PaymentStatus = Field(default=PaymentStatus.UNPAID)
    payment_method: PaymentMethod = Field(default=PaymentMethod.COD)

    status: OrderStatus = Field(default=OrderStatus.PENDING)
    base_delivery_charge: int

    delivery_name: str
    delivery_phone: str

    address_line_2: str | None = None
    address_line_2: str | None

    city: str
    state: str
    country: str
    postal_code: str

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now()
        )
    )


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    order_id: UUID = Field(foreign_key="orders.id", index=True)

    product_id: UUID = Field(foreign_key="product.id", index=True)

    product_name: str

    quantity: int

    price_at_purchase: Decimal = Field(max_digits=10, decimal_places=2)

    selected_size: str

    selected_color: str

    subtotal: Decimal = Field(max_digits=10, decimal_places=2)
