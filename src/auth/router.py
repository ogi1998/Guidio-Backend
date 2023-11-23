from fastapi import APIRouter, HTTPException, status, Request, Response, Depends
from pydantic import EmailStr
from starlette.responses import JSONResponse

from auth import schemas, service, exceptions
from auth.service import get_current_user, get_current_active_user
from core.dependencies import DBDependency
from core.models import User
from core.settings import AUTH_TOKEN
from users.schemas import UserIDSchema, UserReadSchema

router = APIRouter()


@router.post(path="/send_verification_email",
             status_code=status.HTTP_200_OK)
async def send_verification_email(request: Request, email: EmailStr, db=DBDependency):
    user: User = service.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with specified email doesn't exists")
    await service.send_activation_email_to_user(request, user)
    return JSONResponse(content={"detail": "Activation email sent"})


@router.get(path="/verify_email",
            status_code=status.HTTP_200_OK)
def verify_email(token: str, db=DBDependency):
    user = get_current_user(token, db)
    if user is None or user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification failed")
    service.activate_user(user, db)
    return JSONResponse(content={"detail": "Activation successful"}, status_code=status.HTTP_200_OK)


@router.post(path="/register",
             status_code=status.HTTP_201_CREATED,
             response_model=UserIDSchema)
async def register_user(request: Request, data: schemas.RegistrationSchemaUser,
                        db=DBDependency) -> UserIDSchema:
    user_id: int = await service.create_user(request, db, data)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with specified email already exists")
    return UserIDSchema(user_id=user_id)


@router.post(path="/login",
             response_model=UserReadSchema)
def login_user(data: schemas.LoginSchema, response: Response, db=DBDependency) -> UserReadSchema:
    user = service.authenticate_user(data.email, data.password, db)
    if not user:
        raise exceptions.invalid_credentials_exception()
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified")
    token = service.create_auth_token(user.user_id)
    response.set_cookie(key=AUTH_TOKEN, value=token)
    return user


@router.post(path='/logout')
def logout_user():
    response = JSONResponse(content={"message": "User logged out successfully"})
    response.delete_cookie(AUTH_TOKEN)
    response.status_code = status.HTTP_200_OK
    return response


@router.get(path="/token",
            description="Get user object from token",
            response_model=UserReadSchema)
def get_user_from_token(user: User = Depends(get_current_active_user)) -> UserReadSchema:
    return user
