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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)


@app.get("/")
def home():
    return "hello world"
