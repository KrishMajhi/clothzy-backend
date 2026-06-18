from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from .models import (
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    ShippingMethod,
)


class OrderSummaryResponse(BaseModel):
    id: UUID

    order_number: str

    created_at: datetime

    item_count: int

    payment_method: PaymentMethod

    status: OrderStatus

    total_amount: Decimal

    thumbnail: str | None = None

class OrderItemResponse(BaseModel):
    product_id: UUID

    product_name: str

    quantity: int

    price_at_purchase: Decimal

    selected_size: str

    selected_color: str

    subtotal: Decimal
    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: UUID

    user_id: UUID

    subtotal: Decimal

    tax: Decimal

    delivery_charge: Decimal

    shipping_charge: Decimal

    discount: Decimal

    total_amount: Decimal

    shipping_method: ShippingMethod

    payment_method: PaymentMethod

    payment_status: PaymentStatus

    status: OrderStatus

    promo_code: str | None = None

    delivery_name: str
    delivery_phone: str

    address_line_1: str
    address_line_2: str | None = None

    city: str
    state: str
    country: str
    postal_code: str

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class CreateOrderRequest(BaseModel):
    shipping_method: ShippingMethod

    payment_method: PaymentMethod

    delivery_name: str
    delivery_phone: str
    promo_code: str | None = None
    address_line_1: str
    address_line_2: str | None = None

    city: str
    state: str
    country: str
    postal_code: str


class OrderDetailResponse(OrderResponse):
    items: list[OrderItemResponse]
    model_config = {"from_attributes": True}
