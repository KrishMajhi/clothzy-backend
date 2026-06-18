from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from src.db.database import get_session
from src.auth.dependencies import get_current_user

from .schema import (
    CreateOrderRequest,
    OrderResponse,
    OrderDetailResponse,
    OrderSummaryResponse,
)
from .service import OrderService
from fastapi.responses import Response

from .invoice_service import InvoiceService

orderrouter = APIRouter()

orderservice = OrderService()
invoice_service = InvoiceService()


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


@orderrouter.get("/recent", response_model=List[OrderSummaryResponse])
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


@orderrouter.get("/{order_id}/invoice")
async def download_invoice(
    order_id: UUID,
    current_user=Depends(get_current_user),
    session=Depends(get_session),
):
    data = await orderservice.get_order_invoice_data(
        order_id,
        current_user,
        session,
    )

    if not data:
        # raise OrderNotFoundException()
        raise HTTPException(status_code=404, detail={"message":"order not found"})

    order, order_items = data

    pdf_bytes = invoice_service.generate_invoice(
        order,
        order_items,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="invoice-{order.id}.pdf"'
        },
    )
