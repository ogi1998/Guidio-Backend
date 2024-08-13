from pydantic import EmailStr

from core.schemas import UserPasswordSchema, BaseModelSchema
from users import schemas


class RegistrationSchemaUser(schemas.UserBaseSchema, UserPasswordSchema):
    pass

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@guidio.com",
                "first_name": "John",
                "last_name": "Brown",
                "password": "examplePassword123!",
            }
        }


class LoginSchema(BaseModelSchema):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@guidio.com",
                "password": "examplePassword123!",
            }
        }
