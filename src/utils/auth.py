import base64
import datetime

from jose import jwt
from passlib.context import CryptContext

from auth.dependencies import verify_token
from auth.exceptions import UnauthorizedException
from src.config import SECRET_KEY, ALGORITHM
from src.config import TOKEN_EXP_MINUTES

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_base64_subject_from_token(token: str) -> str:
    payload = await verify_token(token)
    sub_base64 = payload.get("sub")
    if sub_base64 is None:
        raise UnauthorizedException()
    return sub_base64


async def get_decoded_sub_from_base64(encoded_token: str) -> int | None:
    """Get decoded subject from base64 encoded"""
    user_id: int = int(base64.b64decode(encoded_token).decode('utf-8'))
    if user_id is None:
        return None
    return user_id


async def create_auth_token(user_id: int) -> str:
    """Create authentication jwt token for a specific user

    Args:
        user_id (int): user id for which jwt token will be created

    Returns:
        jwt token for a specific user
    """
    token_creation_time = datetime.datetime.now(datetime.UTC)
    user_id_base64 = base64.b64encode(str(user_id).encode('utf-8')).decode('utf-8')
    encode = {"sub": user_id_base64, "iat": token_creation_time}
    expire = token_creation_time + datetime.timedelta(minutes=float(TOKEN_EXP_MINUTES))
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_password_hash(password: str) -> str:
    """Return password hash from plain password

    Args:
        password (str): plain password

    Returns:
        string value as password hash
    """
    return bcrypt_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)
