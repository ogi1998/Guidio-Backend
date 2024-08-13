from fastapi import status

from core.exceptions import BaseCustomException


class InstructorsNotFoundException(BaseCustomException):
    def __init__(self, message="Instructors not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class UserNotFoundException(BaseCustomException):
    def __init__(self, message="User not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class ProfessionDoesNotExistException(BaseCustomException):
    def __init__(self, message="Profession does not exist"):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class InvalidCurrentPasswordException(BaseCustomException):
    def __init__(self, message="Invalid current password"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)
