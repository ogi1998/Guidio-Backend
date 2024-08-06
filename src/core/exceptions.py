from fastapi import status


class BaseCustomException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class PageNotFoundException(BaseCustomException):
    def __init__(self, message: str = "Page not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)
