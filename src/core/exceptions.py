from fastapi import HTTPException, status


class BaseCustomException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def non_existent_page_exception():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Requested a non-existent page", )
