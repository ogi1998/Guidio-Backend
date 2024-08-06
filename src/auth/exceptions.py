from fastapi import HTTPException, status

from core.exceptions import BaseCustomException


class UnauthorizedException(BaseCustomException):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class UserDoesNotExist(BaseCustomException):
    def __init__(self, message="User does not exist"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class UserAlreadyExists(BaseCustomException):
    def __init__(self, message="User already exists"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class TokenExpiredException(BaseCustomException):
    def __init__(self, message="Token has expired"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class InvalidCredentials(BaseCustomException):
    def __init__(self, message="Invalid credentials"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class AccountNotVerified(Exception):
    def __init__(self, message="Account not verified"):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = message
        super().__init__(self.message)


class AccountAlreadyVerified(BaseCustomException):
    def __init__(self, message="Account already verified"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class PasswordsDoNotMatch(Exception):
    def __init__(self, message="Email not verified"):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = message
        super().__init__(self.message)


async def invalid_credentials_exception():
    """Return HTTPException 401 for invalid credentials"""
    response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return response


async def user_inactive_exception():
    """Return HTTPException 400 as user is inactive"""
    response = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Inactive user",
    )
    return response
