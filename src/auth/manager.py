from fastapi import Request

from auth import schemas, service
from auth.exceptions import InvalidCredentials, EmailNotVerified
from auth.service import UserAlreadyExists
from core.models import User


class AuthenticationManager:
    def __init__(self):
        self.__auth_service: service.AuthenticationService = service.AuthenticationService()

    async def register_user(self, request: Request,
                            data: schemas.RegistrationSchemaUser) -> User.user_id:
        user: User = await self.__auth_service.get_user_by_email(data.email)
        if user:
            raise UserAlreadyExists
        new_user: User = await self.__auth_service.save_user(data)
        await self.__auth_service.save_user_details(new_user.user_id)
        await self.__auth_service.send_activation_email_to_user(request, new_user)
        return new_user.user_id

    async def login_user(self, email: str, password: str) -> tuple[User, str]:
        try:
            user: User = await self.authenticate_user(email, password)
        except InvalidCredentials as e:
            raise e
        if not user.is_active:
            raise EmailNotVerified
        token: str = await self.__auth_service.create_auth_token(user.user_id)
        return user, token

    async def authenticate_user(self, email: str, password: str) -> User:
        passwords_match = False
        user: User | None = await self.__auth_service.get_user_by_email(email)
        if user:
            passwords_match: bool = await self.__auth_service.verify_password(password,
                                                                              user.password)
        if not user or not passwords_match:
            raise InvalidCredentials
        return user
