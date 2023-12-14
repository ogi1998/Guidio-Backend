from fastapi import Request

from auth import schemas, service
from auth.service import UserAlreadyExists
from core.models import User


class AuthenticationManager:
    def __init__(self):
        self.__auth_service: service.AuthenticationService = service.AuthenticationService()

    async def register_user(self, request: Request,
                            data: schemas.RegistrationSchemaUser) -> User.user_id:
        try:
            user: User = await self.__auth_service.get_user_by_email(data.email)
        except UserAlreadyExists as e:
            raise e

        if user is None:
            new_user: User = await self.__auth_service.save_user(data)
            await self.__auth_service.send_activation_email_to_user(request, new_user)
            return new_user.user_id
