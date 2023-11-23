import os

from fastapi import HTTPException, status, Depends
from jose import jwt, JOSEError


def is_valid_token(token: str) -> dict:
    if not isinstance(token, str):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        payload = jwt.decode(token, key=os.getenv("SECRET_KEY"), algorithms=os.getenv("ALGORITHM"))
        return payload
    except JOSEError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


ValidToken = Depends(is_valid_token)
