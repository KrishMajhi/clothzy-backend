from pydantic import BaseModel

from .models import PaymentMethod, ShippingMethod

class CreateOrderRequest(BaseModel):
    shipping_method: ShippingMethod

    payment_method: PaymentMethod

    delivery_name: str
    delivery_phone: str

    address_line_1: str
    address_line_2: str | None = None

    city: str
    state: str
    country: str
    postal_code: str