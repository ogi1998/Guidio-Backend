import datetime

from fastapi import Request
from sqlalchemy.orm import Session

from auth import schemas
from auth.exceptions import UserDoesNotExistException, UnauthorizedException
from core.constants import ACTIVATE_ACCOUNT_SUBJECT
from core.dependencies import DBDependency
from core.models import User, UserDetail
from core.settings import AUTH_TOKEN
from src.config import TOKEN_EXP_MINUTES
from utils.auth import create_auth_token, get_password_hash, get_base64_subject_from_token, \
    get_decoded_sub_from_base64
from utils.mail.send_mail import send_mail


async def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter(User.email == email).first()


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


async def activate_user(user: User, db: Session) -> None:
    user.is_active = True
    db.commit()
    return


async def get_user_from_token(token: str, db: Session) -> User:
    sub_base64 = await get_base64_subject_from_token(token)
    user_id: int = await get_decoded_sub_from_base64(sub_base64)
    if not user_id:
        raise UnauthorizedException()
    user: User = db.query(User).get(user_id)
    if user is None:
        raise UserDoesNotExistException()
    return user


async def get_user_from_request(request: Request, db: Session) -> User | None:
    user: User = await get_user_from_token(request.cookies.get(AUTH_TOKEN), db)
    return user


async def user_if_profile_is_active(request: Request, db: Session = DBDependency) -> User:
    user: User = await get_user_from_request(request, db)
    if not user.is_active:
        raise UnauthorizedException()
    return user


async def save_user(data: schemas.RegistrationSchemaUser, db: Session) -> User:
    new_user = User()
    new_user.email = data.email
    new_user.first_name = data.first_name
    new_user.last_name = data.last_name
    hashed_password = await get_password_hash(data.password)
    new_user.password = hashed_password
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def save_user_details(user_id: int, db: Session) -> UserDetail:
    # TODO: refactor this function to use schema as data
    user_detail = UserDetail(user_id=user_id)
    db.add(user_detail)
    db.commit()
    return user_detail
