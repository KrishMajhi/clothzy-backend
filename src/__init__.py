from typing import Literal

from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.database import init_db
from .auth.route import user_router
from .product.route import product_router
from .cart.route import cartrouter
from .order.route import orderrouter
from src.auth.model import User
from src.product.model import Product
from src.cart.model import Cart
from fastapi.middleware.cors import CORSMiddleware
from src.errors import register_error_handlers
from src.wishlist.routes import wishlist_router

version = "v0.0.24"


@asynccontextmanager
async def lifespan_func(app: FastAPI):
    print("app is starting!!!!!!!!!!!!!!!!!🏳️🏳️")
    await init_db()
    yield
    print("app is stopping!!!!!!!!!!!!!🔴🚩")


app = FastAPI(
    title="clothzy Backend",
    description="api for ecommerce webiste clothzy",
    version=version,
    lifespan=lifespan_func,
)

app.include_router(user_router, prefix=f"/api/{version}/user", tags=["user"])
app.include_router(product_router, prefix=f"/api/{version}/products", tags=["products"])
app.include_router(cartrouter, prefix=f"/api/{version}/cart", tags=["carts"])
app.include_router(orderrouter, prefix=f"/api/{version}/orders", tags=["orders"])
app.include_router(
    wishlist_router, prefix=f"/api/{version}/wishlist", tags=["wishlist"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://clothzy-frontend-v2.vercel.app",
        "https://clothzy-ecommerce.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)


@app.get("/")
def home() -> Literal["hello world"]:
    return "hello world"
