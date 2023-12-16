from fastapi import HTTPException, status


class UserAlreadyExists(Exception):
    def __init__(self, message="User already exists"):
        self.message = message
        super().__init__(self.message)


class UserDoesNotExist(Exception):
    def __init__(self, message="User does not exist"):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.message = message
        super().__init__(self.message)


class InvalidCredentials(Exception):
    def __init__(self, message="Invalid credentials"):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.message = message
        super().__init__(self.message)


class AccountNotVerified(Exception):
    def __init__(self, message="Account not verified"):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = message
        super().__init__(self.message)


class AccountAlreadyVerified(Exception):
    def __init__(self, message="Account already verified"):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = message
        super().__init__(self.message)


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


async def token_exception():
    """Return HTTPException 401 for invalid token"""
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authorization token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response
