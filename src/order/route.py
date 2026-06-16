from typing import List

from fastapi import APIRouter, Depends

from src.db.database import get_session
from src.auth.dependencies import get_current_user

from .schema import (
    CreateOrderRequest,
    OrderResponse,
    OrderDetailResponse,
    OrderSummaryResponse,
)
from .service import OrderService

orderrouter = APIRouter()

orderservice = OrderService()


@orderrouter.post(
    "/createOrder",
    response_model=OrderResponse,
)
async def create_order(
    data: CreateOrderRequest,
    currentUser=Depends(get_current_user),
    session=Depends(get_session),
):
    return await orderservice.create_userOrder(
        data,
        currentUser,
        session,
    )


@orderrouter.get("/recent",response_model=List[OrderSummaryResponse])
async def get_recent_orders(
    currentUser=Depends(get_current_user),
    session=Depends(get_session),
):
    return await orderservice.get_recent_orders(
        currentUser,
        session,
    )


@orderrouter.get(
    "/allOrders",
    response_model=list[OrderDetailResponse],
)
async def get_all_orders(
    currentUser=Depends(get_current_user),
    session=Depends(get_session),
):
    return await orderservice.get_all_orders(
        currentUser,
        session,
    )


@orderrouter.get(
    "/{order_id}",
    response_model=OrderDetailResponse,
)
async def get_order_by_id(
    order_id: str,
    currentUser=Depends(get_current_user),
    session=Depends(get_session),
):
    return await orderservice.get_order_byId(
        order_id,
        session,
        currentUser,
    )
