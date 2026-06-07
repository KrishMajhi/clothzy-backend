from fastapi import FastAPI

from .exceptions import ClothzyException
from .handlers import clothzy_exception_handler, unhandled_exception_handler


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ClothzyException, clothzy_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)