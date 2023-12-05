import os
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session, Query

from core.constants import MEDIA_ROOT
from core.models import Guide, User, Profession, UserDetail
from core.service import count_number_of_pages
from guides.constants import RetrieveOrder
from guides.schemas import GuideCreateUpdateSchema, GuideListSingleSchema, GuideListReadSchema
from users.schemas import UserListReadSchema


async def prepare_guide_data(data: GuideCreateUpdateSchema) -> GuideCreateUpdateSchema:
    title = data.title.strip()
    content = data.content.strip()
    note = data.note.strip() if data.note else None
    return GuideCreateUpdateSchema(title=title, content=content,
                                   note=note, published=data.published)


def create_upload_path(directory: str, filename: str):
    if not os.path.exists(directory):
        Path(directory).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(directory + filename):
        filename_parts = filename.split(".")
        timestamp = str(int(datetime.now().timestamp()))
        filename = "".join(filename_parts[:-1]) + "_" + timestamp + "." + filename_parts[-1]
    open(f'{directory}{filename}', 'wb').close()
    return directory + filename


def cover_image_upload_path(guide_id: str, filename: str):
    directory = f"{MEDIA_ROOT}/guides/{guide_id}/cover_image/"
    path = create_upload_path(directory, filename)
    path_to_save = 'media' + path.split('media')[1]
    return path_to_save


def count_pages(db: Session, page_size: int):
    count_of_guides: int = db.query(Guide.guide_id) \
        .order_by(desc(Guide.last_modified)).count()
    division: tuple[int, int] = divmod(count_of_guides, page_size)
    pages: int = division[0] + 1 if division[1] else division[0]
    return pages


def count_published_guides_pages(db: Session, page_size: int):
    count_of_guides: int = db.query(Guide.guide_id).filter(Guide.published) \
        .order_by(desc(Guide.last_modified)).count()
    division: tuple[int, int] = divmod(count_of_guides, page_size)
    pages: int = division[0] + 1 if division[1] else division[0]
    return pages


async def get_initial_list_of_guides(db: Session,
                                     search: str = '') -> Query | None:
    guides = db.query(
        Guide.guide_id,
        Guide.title,
        Guide.published,
        Guide.created_at,
        Guide.last_modified,
        Guide.cover_image,
        User.first_name,
        User.last_name,
        UserDetail.avatar,
        User.user_id,
        Profession.name.label('profession')) \
        .filter(Guide.user_id == User.user_id, User.user_id == UserDetail.user_id,
                UserDetail.profession_id == Profession.profession_id,
                func.coalesce(Guide.title, '').ilike(f"%{search}%"),
                )
    return guides


async def get_list_of_guides(db: Session,
                             page: int,
                             page_size: int,
                             sort_order: str = RetrieveOrder.descending,
                             search: str = '',
                             published_only: bool = True,
                             user_id: int = None) -> GuideListReadSchema | None:
    offset: int = page * page_size

    if sort_order == RetrieveOrder.descending:
        order_by_clause = desc(Guide.last_modified)
    else:
        order_by_clause = asc(Guide.last_modified)

    query = await get_initial_list_of_guides(db, search=search)
    if published_only:
        guides = query.filter(Guide.published).order_by(order_by_clause)
    else:
        guides = query.order_by(order_by_clause)
    if user_id:
        guides = guides.filter(Guide.user_id == user_id)
    pages: int = await count_number_of_pages(guides.count(), page_size)
    guides = guides.offset(offset).limit(page_size).all()
    guides_list: list[GuideListSingleSchema] = []
    for record in guides:
        guides_list.append(GuideListSingleSchema(
            guide_id=record[0],
            title=record[1],
            published=record[2],
            created_at=record[3],
            last_modified=record[4],
            cover_image=record[5],
            user=UserListReadSchema(
                first_name=record[6],
                last_name=record[7],
                avatar=record[8],
                user_id=record[9],
                profession=record[10]
            )
        ))
    return GuideListReadSchema(pages=pages, guides=guides_list)


async def search_guides(db: Session, title: str, page: int,
                        page_size: int) -> GuideListReadSchema | None:
    guides = await get_list_of_guides(db, page=page, page_size=page_size, search=title)
    return GuideListReadSchema(pages=guides.pages, guides=guides.guides)


async def get_guides_by_user_id(db: Session,
                                user_id: int,
                                page: int,
                                page_size: int,
                                user: User):
    if user.user_id == user_id:
        guides = await get_list_of_guides(db, page=page, page_size=page_size,
                                          published_only=False, user_id=user_id)
    else:
        guides = await get_list_of_guides(db, page=page, page_size=page_size,
                                          published_only=True, user_id=user_id)
    return guides


async def get_guide_by_id(db: Session, guide_id: int, user: User) -> Guide | None:
    guide: Guide = db.query(Guide).get(guide_id)
    if not guide:
        return None
    if not guide.user_id == user.user_id and not guide.published:
        return None
    return guide


async def save_guide(db: Session,
                     data: GuideCreateUpdateSchema,
                     user_id: int,
                     guide=None) -> Guide:
    if not guide:
        guide = Guide()
    guide.title = data.title
    guide.content = data.content
    guide.note = data.note
    guide.published = data.published
    guide.user_id = user_id
    db.add(guide)
    db.commit()
    db.refresh(guide)
    return guide


async def get_cover_image(guide: Guide) -> str | None:
    if not guide.cover_image:
        return None
    return guide.cover_image


async def save_cover_image(file: UploadFile, db: Session, guide: Guide) -> Guide:
    """Check if cover image exists and create it if not. If it exists then do the update"""

    old_cover_image = guide.cover_image

    file_path = cover_image_upload_path(str(guide.guide_id), file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    guide.cover_image = file_path

    db.add(guide)
    db.commit()

    if old_cover_image and os.path.exists(old_cover_image):
        os.remove(old_cover_image)

    return guide


async def delete_cover_image(db: Session, guide: Guide) -> None:
    image = guide.cover_image

    if image and os.path.exists(image):
        os.remove(image)
    guide.cover_image = None
    db.add(guide)
    db.commit()
    return None


async def delete_guide(db: Session, guide: Guide) -> None:
    await delete_cover_image(db, guide)
    db.delete(guide)
    db.commit()
    return None
