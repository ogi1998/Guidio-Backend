import os
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session

from auth.service import get_password_hash
from core.constants import MEDIA_ROOT
from core.models import User, UserDetail, Profession, Guide
from core.service import count_number_of_pages
from users.schemas import UserProfileUpdateSchema, UserPasswordUpdateSchema, UserDetailUpdateSchema, \
    UserReadSchemaWithPages


async def get_instructors_by_search(db: Session, search: str):
    return db.query(User).filter(or_(
        User.first_name.ilike(f"%{search}%"),
        User.last_name.ilike(f"%{search}%")
    )).join(UserDetail).filter(UserDetail.is_instructor)


async def get_paginated_instructors_by_search(db: Session, page: int, page_size: int, search: str):
    offset: int = page * page_size
    instructors_from_search = await get_instructors_by_search(db, search)
    return instructors_from_search.offset(offset).limit(page_size).all()


async def get_number_of_instructors_from_search(db: Session,
                                                search: str,
                                                page_size: int):
    instructors_from_search = await get_instructors_by_search(db, search)
    count_of_instructors = len(instructors_from_search.all())
    division: tuple[int, int] = divmod(count_of_instructors, page_size)
    pages: int = division[0] + 1 if division[1] else division[0]
    return pages


async def create_upload_path(directory: str, filename: str):
    if not os.path.exists(directory):
        Path(directory).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(directory + filename):
        filename_parts = filename.split(".")
        timestamp = str(int(datetime.now().timestamp()))
        filename = "".join(filename_parts[:-1]) + "_" + timestamp + "." + filename_parts[-1]
    open(f'{directory}{filename}', 'wb').close()
    return directory + filename


async def avatar_upload_path(first_name: str, last_name: str, filename: str):
    user_name = first_name + "_" + last_name
    directory = f"{MEDIA_ROOT}/users/{user_name}/avatar/"

    path = await create_upload_path(directory, filename)
    path_to_save = 'media' + path.split('media')[1]

    return path_to_save


async def cover_image_upload_path(first_name: str, last_name: str, filename: str):
    user_name = first_name + "_" + last_name
    directory = f"{MEDIA_ROOT}/users/{user_name}/cover_image/"

    path = await create_upload_path(directory, filename)
    path_to_save = 'media' + path.split('media')[1]
    return path_to_save


async def get_avatar(user: User) -> str | None:
    if not user.user_details:
        return None
    return user.user_details.avatar


async def save_avatar(file: UploadFile, db: Session, user: User) -> User:
    """Check if avatar exists and create it if not. If it exists then do the update"""

    old_user_avatar = user.user_details.avatar

    file_path = await avatar_upload_path(user.first_name, user.last_name, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    user.user_details.avatar = file_path

    db.add(user)
    db.commit()

    if old_user_avatar and os.path.exists(old_user_avatar):
        os.remove(old_user_avatar)

    return user


async def delete_avatar(db: Session, user: User):
    avatar = user.user_details.avatar

    if os.path.exists(avatar):
        os.remove(avatar)
    user.user_details.avatar = None
    db.add(user)
    db.commit()
    return None


async def get_cover_image(user: User) -> str | None:
    if not user.user_details:
        return
    return user.user_details.cover_image


async def save_cover_image(file: UploadFile, db: Session, user: User) -> User:
    """Check if cover image exists and create it if not. If it exists then do the update"""

    old_cover_image = user.user_details.cover_image

    file_path = await cover_image_upload_path(user.first_name, user.last_name, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    user.user_details.cover_image = file_path

    db.add(user)
    db.commit()

    if old_cover_image and os.path.exists(old_cover_image):
        os.remove(old_cover_image)

    return user


async def delete_cover_image(db: Session, user: User):
    image = user.user_details.cover_image

    if os.path.exists(image):
        os.remove(image)
    user.user_details.cover_image = None
    db.add(user)
    db.commit()
    return None


async def get_paginated_instructors(db: Session, offset, limit) -> UserReadSchemaWithPages:
    offset: int = offset * limit
    all_instructors = db.query(User).join(User.user_details) \
        .filter(UserDetail.is_instructor)
    paginated_instructors: list[User] = all_instructors.offset(offset).limit(limit).all()
    count_of_instructors: int = all_instructors.count()
    pages: int = await count_number_of_pages(count_of_instructors, limit)
    return UserReadSchemaWithPages(pages=pages, users=paginated_instructors)


async def get_profession_by_id(db: Session, profession_id: int) -> Profession | None:
    profession = db.query(Profession).get(profession_id)
    return profession


async def get_professions_by_name(db: Session, name: str) -> list[Profession]:
    professions = db.query(Profession).filter(Profession.name.ilike(f'%{name}%')).all()
    return professions


async def get_user_profile_by_id(user_id: int, db: Session) -> User | None:
    user = db.query(User).get(user_id)
    return user


async def update_user_details(data: UserDetailUpdateSchema, db: Session, db_user: User):
    user_detail: UserDetail = db.query(UserDetail) \
        .filter(UserDetail.user_id == db_user.user_id).first()
    if user_detail:
        user_detail.linkedin = data.linkedin
        user_detail.github = data.github
        user_detail.website = data.website
        user_detail.is_instructor = data.is_instructor
        user_detail.bio = data.bio
        user_detail.profession_id = data.profession_id
    else:
        new_user_detail = UserDetail(user_id=db_user.user_id,
                                     linkedin=data.linkedin,
                                     github=data.github,
                                     website=data.website,
                                     is_instructor=data.is_instructor,
                                     bio=data.bio,
                                     profession_id=data.profession_id)
        db.add(new_user_detail)
    db.commit()


async def update_user_profile(data: UserProfileUpdateSchema,
                              db: Session, db_user: User) -> User:
    db_user.email = data.email
    db_user.first_name = data.first_name
    db_user.last_name = data.last_name

    await update_user_details(data.user_details, db, db_user)
    # Update guides if is_instructor is set to false
    if not data.user_details.is_instructor:
        guides = db.query(Guide).filter(Guide.user_id == db_user.user_id).all()
        if guides:
            for guide in guides:
                guide.published = False

    db.commit()
    db.refresh(db_user)
    return db_user


async def delete_user_profile(db: Session, user_id: int) -> None:
    user: User = db.query(User).get(user_id)
    db.delete(user)
    db.commit()
    return None


async def update_user_password(db: Session,
                               data: UserPasswordUpdateSchema,
                               user: User) -> tuple[User, UserDetail]:
    hashed_password = await get_password_hash(data.password)
    user.password = hashed_password
    db.commit()
    db.refresh(user)
    return user
