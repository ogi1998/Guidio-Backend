from fastapi import APIRouter, status, Request, Response, Depends
from pydantic import EmailStr
from starlette.responses import JSONResponse

from auth import schemas, manager
from core.models import User
from core.settings import AUTH_TOKEN
from users.schemas import UserIDSchema, UserReadSchema

router = APIRouter()
auth_manager = manager.AuthenticationManager()


@router.post(path="/send_verification_email",
             status_code=status.HTTP_200_OK)
async def send_verification_email(request: Request, email: EmailStr):
    await auth_manager.send_verification_email(request, email)
    return JSONResponse(content={"detail": "Activation email sent"})


@router.get(path="/activate_user",
            status_code=status.HTTP_200_OK)
async def activate_user(token: str):
    await auth_manager.activate_user(token)
    return JSONResponse(content={"detail": "Activation successful"}, status_code=status.HTTP_200_OK)


@router.post(path="/register",
             status_code=status.HTTP_201_CREATED,
             response_model=UserIDSchema)
async def register_user(request: Request, data: schemas.RegistrationSchemaUser) -> UserIDSchema:
    user_id: int = await auth_manager.register_user(request, data)
    return UserIDSchema(user_id=user_id)


@router.post(path="/login",
             response_model=UserReadSchema)
async def login_user(data: schemas.LoginSchema, response: Response) -> UserReadSchema:
    user, token = await auth_manager.login_user(data.email, data.password)
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
        user: User = Depends()) -> UserReadSchema:
    return user
