from fastapi import HTTPException, status

from core.exceptions import BaseCustomException


class UnauthorizedException(BaseCustomException):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class UserDoesNotExistException(BaseCustomException):
    def __init__(self, message="User does not exist"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class UserAlreadyExistsException(BaseCustomException):
    def __init__(self, message="User already exists"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class TokenExpiredException(BaseCustomException):
    def __init__(self, message="Token has expired"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class InvalidCredentialsException(BaseCustomException):
    def __init__(self, message="Invalid credentials"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class AccountNotVerifiedException(BaseCustomException):
    def __init__(self, message="Account not verified"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class AccountAlreadyVerifiedException(BaseCustomException):
    def __init__(self, message="Account already verified"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)
