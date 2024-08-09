from fastapi import APIRouter, status, Request, Response, Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from auth import schemas, manager, service
from core.dependencies import DBDependency
from core.models import User
from core.settings import AUTH_TOKEN
from users.schemas import UserIDSchema, UserReadSchema

router = APIRouter()


@router.post(path="/send_verification_email",
             status_code=status.HTTP_200_OK)
async def send_verification_email(request: Request, email: EmailStr, db: Session = DBDependency):
    await manager.send_verification_email(request, email, db)
    return JSONResponse(content={"detail": "Activation email sent"})


@router.get(path="/activate_user",
            status_code=status.HTTP_200_OK)
async def activate_user(token: str, db: Session = DBDependency):
    await manager.activate_user(token, db)
    return JSONResponse(content={"detail": "Activation successful"}, status_code=status.HTTP_200_OK)


@router.post(path="/register",
             status_code=status.HTTP_201_CREATED,
             response_model=UserIDSchema)
async def register_user(request: Request, data: schemas.RegistrationSchemaUser,
                        db: Session = DBDependency) -> UserIDSchema:
    user_id: int = await manager.register_user(request, data, db)
    return UserIDSchema(user_id=user_id)


@router.post(path="/login",
             response_model=UserReadSchema)
async def login_user(data: schemas.LoginSchema, response: Response,
                     db: Session = DBDependency) -> UserReadSchema:
    user, token = await manager.login_user(data.email, data.password, db)
    response.set_cookie(key=AUTH_TOKEN, value=token)
    return user


@router.post(path='/logout')
async def logout_user():
    response = JSONResponse(content={"message": "Logged out successfully"},
                            status_code=status.HTTP_200_OK)
    response.delete_cookie(AUTH_TOKEN)
    return response


@router.get(path="/user_info",
            description="Get user object from token",
            response_model=UserReadSchema)
async def get_user_from_token(
        user: User = Depends(service.user_if_profile_is_active)) -> UserReadSchema:
    return user
