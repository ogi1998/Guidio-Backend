from fastapi import status

from core.exceptions import BaseCustomException


class GuidesNotFoundException(BaseCustomException):
    def __init__(self, message="Guides not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class GuideNotFoundException(BaseCustomException):
    def __init__(self, message="Guide not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class NotInstructorException(BaseCustomException):
    """Raises when user is not an instructor"""

    def __init__(self, message="You are not an instructor"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)
