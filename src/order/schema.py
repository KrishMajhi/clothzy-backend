from pydantic import BaseModel

from .models import PaymentMethod, ShippingMethod

class CreateOrderRequest(BaseModel):
    shipping_method: ShippingMethod

    payment_method: PaymentMethod
    deliveryEligible:False

    
    delivery_name: str
    delivery_phone: str
    promo_code:str|None=None
    address_line_1: str
    address_line_2: str | None = None

    city: str
    state: str
    country: str
    postal_code: str