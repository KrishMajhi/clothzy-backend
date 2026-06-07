from fastapi import status


class ClothzyException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "An unexpected error occurred"

    def __init__(self, detail: str | None = None):
        self.detail = detail if detail is not None else self.__class__.detail
        super().__init__(self.detail)


# ── Auth ──────────────────────────────────────────────────────────────────────

class InvalidTokenException(ClothzyException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Invalid or expired token"


class InvalidAccessTokenException(ClothzyException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Please provide an access token"


class InvalidRefreshTokenException(ClothzyException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Please provide a refresh token"


class UserNotFoundException(ClothzyException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found"


class UnauthorizedException(ClothzyException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token"


class ForbiddenException(ClothzyException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "You don't have access to this resource"


class UserAlreadyExistsException(ClothzyException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "User with this email already exists"


class InvalidCredentialsException(ClothzyException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid email or password"


class OldPasswordIncorrectException(ClothzyException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Old password is incorrect"


class SamePasswordException(ClothzyException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "New password cannot be the same as the old password"


# ── Product ───────────────────────────────────────────────────────────────────

class ProductNotFoundException(ClothzyException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Product not found"


class GenderRequiredException(ClothzyException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "gender query parameter is required"


# ── Cart ──────────────────────────────────────────────────────────────────────

class CartItemNotFoundException(ClothzyException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Cart item not found"


class InvalidQuantityException(ClothzyException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Quantity must be greater than 0"


class InsufficientStockException(ClothzyException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, stock: int):
        super().__init__(detail=f"Only {stock} items available in stock")


class QuantityLimitExceededException(ClothzyException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, max_qty: int):
        super().__init__(detail=f"Maximum allowed quantity is {max_qty}")


class InvalidColorException(ClothzyException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid color selected"


class InvalidSizeException(ClothzyException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid size selected"


class ProductAlreadyInCartException(ClothzyException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Product already in cart"