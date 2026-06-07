from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends

from src.auth.dependencies import Role_checker
from src.db.database import get_session
from .schemas.productmodel import (
    ProductCategory,
    Gender,
    ProductCreateModel,
    ProductListResponseModel,
    ProductResponseModel,
    ProductSort,
    ProductUpdateModel,
)
from .model import Product
from .service import ProductService

from src.errors import (
    ProductNotFoundException,
    GenderRequiredException,
)

product_router = APIRouter()
productService = ProductService()


# ════════════════════════════════════════════════════════════
# STATIC METADATA
# ════════════════════════════════════════════════════════════
@product_router.get("/product/metadata")
async def get_product_metadata():
    return {
        "categories": [c.value for c in ProductCategory],
        "genders": [g.value for g in Gender],
        "sort_by": [s.value for s in ProductSort],
    }


# ════════════════════════════════════════════════════════════
# FILTER METADATA
# ════════════════════════════════════════════════════════════
@product_router.get("/filter_metadata")
async def get_filter_metadata(
    gender: str = None,
    session=Depends(get_session),
):
    if not gender:
        raise GenderRequiredException()

    metadata = await productService.get_filtermetadata(
        session=session,
        gender_category=gender,
    )
    return metadata


# ════════════════════════════════════════════════════════════
# ALL PRODUCTS
# ════════════════════════════════════════════════════════════
@product_router.get("/all_products")
async def get_products(
    category: Optional[str] = None,
    gender: Optional[str] = None,
    material: Optional[str] = None,
    sort_by: Optional[str] = None,
    max_range: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
    sizes: Optional[str] = None,
    colors: Optional[str] = None,
    session=Depends(get_session),
):
    page = max(page, 1)
    limit = max(1, min(limit, 100))

    valid_sorts = {s.value for s in ProductSort}
    if sort_by not in valid_sorts:
        sort_by = None

    products = await productService.get_all_products(
        session=session,
        material=material,
        category=category,
        gender=gender,
        sort_by=sort_by,
        search=search,
        limit=limit,
        page=page,
        max_range=max_range,
        sizes=sizes,
        colors=colors,
    )

    count = await productService.count_products(
        session=session,
        material=material,
        category=category,
        gender=gender,
        max_range=max_range,
        search=search,
        sizes=sizes,
        colors=colors,
    )

    total_pages = max(1, -(-count // limit))

    return {
        "items": products,
        "total": count,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


# ════════════════════════════════════════════════════════════
# SINGLE PRODUCT
# ════════════════════════════════════════════════════════════
@product_router.get("/get_product/{product_id}", response_model=ProductResponseModel)
async def get_product(product_id: uuid.UUID, session=Depends(get_session)):
    product = await productService.get_product_by_uid(session, product_id)
    if product:
        return product
    raise ProductNotFoundException()


# ════════════════════════════════════════════════════════════
# CREATE PRODUCT
# ════════════════════════════════════════════════════════════
@product_router.post("/create_product", response_model=ProductResponseModel)
async def create_product(
    admin_product: ProductCreateModel,
    _: bool = Depends(Role_checker(["admin"])),
    session=Depends(get_session),
):
    return await productService.create_product(session, admin_product)


# ════════════════════════════════════════════════════════════
# UPDATE PRODUCT
# ════════════════════════════════════════════════════════════
@product_router.patch("/update_product/{p_id}", response_model=ProductResponseModel)
async def update_product(
    p_id: uuid.UUID,
    updated_product: ProductUpdateModel,
    _: bool = Depends(Role_checker(["admin"])),
    session=Depends(get_session),
):
    result = await productService.update_product(session, p_id, updated_product)
    if result:
        return result
    raise ProductNotFoundException()


# ════════════════════════════════════════════════════════════
# DELETE PRODUCT
# ════════════════════════════════════════════════════════════
@product_router.delete("/delete_product/{p_id}")
async def delete_product(
    p_id: uuid.UUID,
    _: bool = Depends(Role_checker(["admin"])),
    session=Depends(get_session),
):
    deleted = await productService.delete_product(session, p_id)
    if deleted:
        return {"detail": "Product deleted successfully"}
    raise ProductNotFoundException()