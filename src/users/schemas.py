from pydantic import EmailStr, Field

from core.schemas import BaseModelSchema, UserPasswordSchema


class ProfessionReadSchema(BaseModelSchema):
    profession_id: int
    name: str

    class Config:
        orm_mode = True


class UserDetailSchema(BaseModelSchema):
    linkedin: str | None
    github: str | None
    website: str | None
    is_instructor: bool
    bio: str | None
    avatar: str | None
    cover_image: str | None
    profession: ProfessionReadSchema | None

    class Config:
        orm_mode = True


class UserAvatarSchema(BaseModelSchema):
    avatar: str | None

    class Config:
        orm_mode = True


class UserCoverImageSchema(BaseModelSchema):
    cover_image: str | None

    class Config:
        orm_mode = True


class UserIDSchema(BaseModelSchema):
    user_id: int


class UserBaseSchema(BaseModelSchema):
    email: EmailStr
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=150)


class UserDetailUpdateSchema(BaseModelSchema):
    linkedin: str = Field(max_length=255)
    github: str = Field(max_length=255)
    website: str = Field(max_length=255)
    is_instructor: bool = False
    bio: str | None
    profession_id: int | None

    class Config:
        schema_extra = {
            "example": {
                "linkedin": "linkedin.com",
                "github": "github.com",
                "website": "google.com",
                "is_instructor": False,
                "bio": "This is an example of bio",
                "profession_id": 1
            }
        }


class UserProfileUpdateSchema(UserBaseSchema):
    user_details: UserDetailUpdateSchema

    class Config:
        schema_extra = {
            "example": {
                "email": "john@guidio.com",
                "first_name": "John",
                "last_name": "Brown",
                "user_details": UserDetailUpdateSchema.Config.schema_extra['example']
            }
        }


class UserListReadSchema(BaseModelSchema):
    user_id: int
    avatar: str | None
    cover_image: str | None
    profession: str | None


class UserReadSchema(UserBaseSchema):
    user_id: int
    is_active: bool
    user_details: UserDetailSchema | None

    class Config:
        orm_mode = True


class UserPasswordUpdateSchema(UserPasswordSchema):
    current_password: str

    class Config:
        schema_extra = {
            "example": {
                "current_password": "MyPa$$123!",
                "password": "MyPa$$123!",
            }
        }
