from fastapi import HTTPException, status

from core.exceptions import BaseCustomException


class GuidesNotFound(BaseCustomException):
    def __init__(self, message="Guides not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class NotInstructorException(BaseCustomException):
    """Raises when user is not an instructor"""
    def __init__(self, message="You are not an instructor"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


async def not_instructor_exception():
    """Raises when user is not an instructor"""
    exception = HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                              detail="You are not an instructor")
    return exception
