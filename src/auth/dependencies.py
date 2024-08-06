import os

from jose import jwt, JOSEError

from auth.exceptions import UnauthorizedException, TokenExpiredException


async def get_decoded_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, key=os.getenv("SECRET_KEY"),
                             algorithms=[os.getenv("ALGORITHM")])
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except JOSEError:
        raise UnauthorizedException()
