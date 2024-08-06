import datetime

from fastapi import Request
from sqlalchemy.orm import Session

from auth import schemas
from auth.dependencies import get_decoded_token
from auth.exceptions import UnauthorizedException, UserDoesNotExistException
from core.constants import ACTIVATE_ACCOUNT_SUBJECT
from core.dependencies import get_db
from core.models import User, UserDetail
from core.settings import AUTH_TOKEN
from src.config import TOKEN_EXP_MINUTES
from utils.auth import get_decoded_sub_from_base64, create_auth_token, get_password_hash
from utils.mail.send_mail import send_mail


class AuthenticationService:

    def __init__(self):
        self.__db: Session = get_db()

    async def save_user(self,
                        data: schemas.RegistrationSchemaUser) -> User:
        new_user = User()
        new_user.email = data.email
        new_user.first_name = data.first_name
        new_user.last_name = data.last_name
        hashed_password = await get_password_hash(data.password)
        new_user.password = hashed_password
        self.__db.add(new_user)
        self.__db.commit()
        self.__db.refresh(new_user)
        return new_user

    async def save_user_details(self, user_id: int) -> UserDetail:
        # TODO: refactor this function to use schema as data
        user_detail = UserDetail(user_id=user_id)
        self.__db.add(user_detail)
        self.__db.commit()
        return user_detail

    async def get_user_by_email(self, email: str) -> User | None:
        return self.__db.query(User).filter(User.email == email).first()

    @staticmethod
    async def send_activation_email_to_user(request: Request, user: User):
        token = await create_auth_token(user.user_id)
        base_url = str(request.base_url)
        verification_url: str = f"{base_url}auth/verify_email?token={token}"
        expiration_time: datetime = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            minutes=int(TOKEN_EXP_MINUTES))
        await send_mail(subject=ACTIVATE_ACCOUNT_SUBJECT,
                        recipients=[user.email],
                        body={"first_name": user.first_name, "url": verification_url,
                              "expire_at": expiration_time.strftime("%Y-%m-%d %H:%M:%S")},
                        template_name="activation_email.html")

    async def get_user_from_token(self, token: str) -> User:
        payload = await get_decoded_token(token)
        user_id_base64 = payload.get("sub")
        user_id = await get_decoded_sub_from_base64(user_id_base64)
        if user_id is None:
            raise UnauthorizedException()
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise UserDoesNotExistException()
        return user

    async def is_profile_active(self, request: Request):
        current_user = await self.get_user_from_token(request.cookies.get(AUTH_TOKEN))
        if not current_user.is_active:
            raise UnauthorizedException()
        return current_user

    async def activate_user(self, user: User) -> None:
        user.is_active = True
        self.__db.commit()
        return

    async def get_user_by_id(self, user_id: int) -> User | None:
        return self.__db.query(User).get(user_id)
