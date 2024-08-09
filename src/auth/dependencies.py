import os

from jose import jwt, JOSEError

from auth.exceptions import UnauthorizedException, TokenExpiredException


async def verify_token(token: str) -> dict:
    if not isinstance(token, str):
        raise UnauthorizedException()
    try:
        payload = jwt.decode(token, key=os.getenv("SECRET_KEY"),
                             algorithms=[os.getenv("ALGORITHM")])
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except JOSEError:
        raise UnauthorizedException()
