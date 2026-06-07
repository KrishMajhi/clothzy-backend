import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from .exceptions import ClothzyException

logger = logging.getLogger(__name__)


async def clothzy_exception_handler(request: Request, exc: ClothzyException) -> JSONResponse:
    logger.error(
        "ClothzyException [%s %s] %s — %s",
        request.method,
        request.url.path,
        exc.__class__.__name__,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception [%s %s]", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )