from fastapi import Request
from sqlalchemy.orm import Session

from auth import schemas, service
from auth.exceptions import InvalidCredentialsException, AccountNotVerifiedException, \
    UserAlreadyExistsException, \
    UserDoesNotExistException, AccountAlreadyVerifiedException
from core.models import User
from utils.auth import create_auth_token, verify_password


async def activate_user(token: str, db: Session):
    user = await service.get_user_from_token(token, db)
    if user.is_active:
        raise AccountAlreadyVerifiedException()
    await service.activate_user(user, db)
    return user


async def register_user(request: Request,
                        data: schemas.RegistrationSchemaUser, db: Session) -> User.user_id:
    user: User = await service.get_user_by_email(data.email, db)
    if user:
        raise UserAlreadyExistsException()
    new_user: User = await service.save_user(data, db)
    await service.save_user_details(new_user.user_id, db)
    await service.send_activation_email_to_user(request, new_user)
    return new_user.user_id


async def login_user(email: str, password: str, db: Session) -> tuple[User, str]:
    user: User = await authenticate_user(email, password, db)
    if not user.is_active:
        raise AccountNotVerifiedException()
    token: str = await create_auth_token(user.user_id)
    return user, token


async def authenticate_user(email: str, password: str, db: Session) -> User:
    user: User | None = await service.get_user_by_email(email, db)
    if not user:
        raise UserDoesNotExistException()
    passwords_match: bool = await verify_password(password,
                                                  user.password)
    if not passwords_match:
        raise InvalidCredentialsException()
    return user


async def send_verification_email(request: Request, email: str, db: Session) -> None:
    user: User = await service.get_user_by_email(email, db)
    if user is None:
        raise UserDoesNotExistException()
    elif user.is_active:
        raise AccountAlreadyVerifiedException()
    await service.send_activation_email_to_user(request, user)
    return None
