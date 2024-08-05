import os

from fastapi import Depends
from jose import jwt, JOSEError


async def get_decoded_token(token: str) -> dict:
    if not isinstance(token, str):
        raise ValueError
    try:
        payload = jwt.decode(token, key=os.getenv("SECRET_KEY"), algorithms=os.getenv("ALGORITHM"))
        return payload
    except JOSEError as e:
        raise e


ValidToken = Depends(get_decoded_token)  # TODO: Remove when there is no usage
