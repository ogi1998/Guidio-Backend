from fastapi import status


class BaseCustomException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ImageNotFoundException(BaseCustomException):
    def __init__(self, message="Image not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)
