from fastapi import Request

from auth import schemas, service
from auth.exceptions import InvalidCredentials, AccountNotVerified, UserAlreadyExists, \
    UserDoesNotExist, AccountAlreadyVerified
from core.models import User
from utils.auth import create_auth_token, verify_password


class AuthenticationManager:
    def __init__(self):
        self.__auth_service: service.AuthenticationService = service.AuthenticationService()

    async def register_user(self, request: Request,
                            data: schemas.RegistrationSchemaUser) -> User.user_id:
        user: User = await self.__auth_service.get_user_by_email(data.email)
        if user:
            raise UserAlreadyExists()
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
            raise AccountNotVerified
        token: str = await create_auth_token(user.user_id)
        return user, token

    async def authenticate_user(self, email: str, password: str) -> User:
        user: User | None = await self.__auth_service.get_user_by_email(email)
        if not user:
            raise UserDoesNotExist()
        passwords_match: bool = await verify_password(password,
                                                      user.password)
        if not passwords_match:
            raise InvalidCredentials()
        return user

    async def send_verification_email(self, request: Request, email: str) -> None:
        user: User = await self.__auth_service.get_user_by_email(email)
        if user is None:
            raise UserDoesNotExist()
        elif user.is_active:
            raise AccountAlreadyVerified()
        await self.__auth_service.send_activation_email_to_user(request, user)
        return None

    async def activate_user(self, token: str):
        user = await self.__auth_service.get_user_from_token(token)
        await self.__auth_service.activate_user(user)
        return user
