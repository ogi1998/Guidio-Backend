import base64
import re
from datetime import datetime, timedelta
from typing import Match

from fastapi import Request, HTTPException
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from auth import schemas
from auth.dependencies import get_decoded_token
from auth.exceptions import invalid_credentials_exception, token_exception, user_inactive_exception
from core.constants import ACTIVATE_ACCOUNT_SUBJECT
from core.dependencies import get_db
from core.models import User, UserDetail
from core.settings import AUTH_TOKEN
from src.config import SECRET_KEY, ALGORITHM, TOKEN_EXP_MINUTES
from utils.mail.send_mail import send_mail


class AuthenticationService:

    def __init__(self):
        self.__db: Session = get_db()
        self.__bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # TODO: Move this function to users
    async def save_user(self,
                        data: schemas.RegistrationSchemaUser) -> User:
        new_user = User()
        new_user.email = data.email
        new_user.first_name = data.first_name
        new_user.last_name = data.last_name
        hashed_password = await self.get_password_hash(data.password)
        new_user.password = hashed_password
        self.__db.add(new_user)
        self.__db.commit()
        self.__db.refresh(new_user)
        return new_user

    # TODO: Move this function to users
    async def save_user_details(self, user_id: int) -> UserDetail:
        # TODO: refactor this function to use schema as data
        user_detail = UserDetail(user_id=user_id)
        self.__db.add(user_detail)
        self.__db.commit()
        return user_detail

    # TODO: Move this function to users
    async def get_user_by_email(self, email: str) -> User | None:
        return self.__db.query(User).filter(User.email == email).first()

    # TODO: Move this function to users
    async def send_activation_email_to_user(self, request: Request, user: User):
        token = await self.create_auth_token(user.user_id)
        base_url = str(request.base_url)
        verification_url: str = f"{base_url}auth/verify_email?token={token}"
        expiration_time: datetime = datetime.utcnow() + timedelta(minutes=int(TOKEN_EXP_MINUTES))
        try:
            await send_mail(subject=ACTIVATE_ACCOUNT_SUBJECT,
                            recipients=[user.email],
                            body={"first_name": user.first_name, "url": verification_url,
                                  "expire_at": expiration_time.strftime("%Y-%m-%d %H:%M:%S")},
                            template_name="activation_email.html")
        except Exception as e:
            raise e

    async def get_password_hash(self, password: str) -> str:
        """Return password hash from plain password

        Args:
            password (str): plain password

        Returns:
            string value as password hash
        """
        return self.__bcrypt_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.__bcrypt_context.verify(plain_password, hashed_password)

    @staticmethod
    async def find_detail_in_error(substring: str, message: str) -> Match[str] | None:
        """Handle search for substring in error message. Used in exception handling.

        Args:
            substring (str): specific text to search for, e.g. "email"
            message (str): message provided to search a substring in

        Returns:
            Match[str]: Match if string is found
            None: if string isn't found
        """
        return re.search(str(substring), str(message))

    @staticmethod
    async def create_auth_token(user_id: int) -> str:
        """Create authentication jwt token for a specific user

        Args:
            user_id (int): user id for which jwt token will be created

        Returns:
            jwt token for a specific user
        """
        token_creation_time = datetime.utcnow()
        user_id_base64 = base64.b64encode(str(user_id).encode('utf-8')).decode('utf-8')
        encode = {"sub": user_id_base64, "iat": token_creation_time}
        expire = token_creation_time + timedelta(minutes=float(TOKEN_EXP_MINUTES))
        encode.update({"exp": expire})
        return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    # TODO: Move this function to users
    async def get_current_user(self, token: str):
        try:
            payload = await get_decoded_token(token)
        except ValueError as e:
            raise e

        user_id_base64 = payload.get("sub")
        user_id = int(base64.b64decode(user_id_base64).decode('utf-8'))
        if user_id is None:
            raise await invalid_credentials_exception()
        user: User = await self.get_user_by_id(user_id)
        if user is None:
            raise await invalid_credentials_exception()
        return user

    # TODO: Move this function to users
    async def get_current_active_user(self, request: Request, db=DBDependency):
        current_user = await self.get_current_user(request.cookies.get(AUTH_TOKEN), db)
        if not current_user.is_active:
            raise await user_inactive_exception()
        return current_user

    # TODO: Move this function to users
    async def activate_user(self, user: User) -> None:
        user.is_active = True
        self.__db.commit()
        return


    async def get_user_by_id(self, user_id: int):
        return self.__db.query(User).get(user_id)
