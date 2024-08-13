from fastapi import UploadFile
from sqlalchemy.orm import Session

from auth.exceptions import UnauthorizedException
from core.exceptions import ImageNotFoundException
from core.models import User
from users import service, schemas, exceptions
from utils.auth import verify_password


async def get_professions_by_name(name: str, db: Session) -> list[schemas.ProfessionReadSchema]:
    professions = await service.get_professions_by_name(name, db)
    return professions


async def get_instructors(page: int, page_size: int, db: Session):
    instructors = await service.get_paginated_instructors(db, page - 1, page_size)
    if page > instructors.pages:
        raise exceptions.InstructorsNotFoundException()
    return instructors


async def search_instructors(search: str, page: int, page_size: int, db: Session):
    total_pages = await service.get_number_of_instructors_from_search(db, search, page_size)
    if page > total_pages:
        raise exceptions.InstructorsNotFoundException()
    instructors = await service.get_paginated_instructors_by_search(db, page=page - 1,
                                                                    page_size=page_size,
                                                                    search=search)
    return schemas.UserReadSchemaWithPages(pages=total_pages, users=instructors)


async def get_user_avatar(user: User):
    avatar = await service.get_avatar(user)
    if avatar is None:
        raise ImageNotFoundException()
    return schemas.UserAvatarSchema(avatar=avatar)


async def save_user_avatar(file: UploadFile, db: Session, user: User) -> schemas.UserReadSchema:
    saved = await service.save_avatar(file, db, user)
    return saved


async def delete_user_avatar(db: Session, user: User):
    avatar = user.user_details.avatar
    if avatar is None:
        raise ImageNotFoundException()
    await service.delete_avatar(db, user)
    return None


async def get_user_cover_image(user: User):
    image = await service.get_cover_image(user)
    if image is None:
        raise ImageNotFoundException()
    return schemas.UserCoverImageSchema(cover_image=image)


async def save_user_cover_image(file: UploadFile, db: Session, user: User):
    saved = await service.save_cover_image(file, db, user)
    return saved


async def delete_user_cover_image(db: Session, user: User):
    image = user.user_details.cover_image
    if image is None:
        raise ImageNotFoundException()
    await service.delete_cover_image(db, user)
    return None


async def get_user_profile_by_id(user_id: int, db: Session):
    user = await service.get_user_profile_by_id(user_id, db)
    if not user:
        raise exceptions.UserNotFoundException()
    return user


async def update_user_profile(user_id: int, data: schemas.UserProfileUpdateSchema, db: Session,
                              user: User):
    if user_id != user.user_id:
        raise UnauthorizedException()
    if data.user_details.profession_id:
        profession = await service.get_profession_by_id(db, data.user_details.profession_id)
        if not profession:
            raise exceptions.UserNotFoundException()
    await service.update_user_profile(data, db, user)
    return user


async def delete_user_profile(user_id: int, db: Session, user: User) -> None:
    if not user or user_id != user.user_id:
        raise UnauthorizedException()
    return await service.delete_user_profile(db, user_id)


async def update_user_password(user_id: int, data: schemas.UserPasswordUpdateSchema, db: Session,
                               user: User):
    if user_id != user.user_id:
        raise UnauthorizedException()
    if not await verify_password(data.current_password, user.password):
        raise exceptions.InvalidCurrentPasswordException()
    updated_user = await service.update_user_password(db, data, user)
    return updated_user
