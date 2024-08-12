import os
import shutil

from fastapi import UploadFile
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session, Query

from core.models import Guide, User, Profession, UserDetail
from core.service import count_number_of_pages
from guides.constants import RetrieveOrder
from guides.schemas import GuideCreateUpdateSchema, GuideListSingleSchema, GuideListReadSchema
from users.schemas import UserListReadSchema
from utils.guides import get_featured_image_upload_path


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
    guides_list = [
        GuideListSingleSchema(
            **{
                "guide_id": record.guide_id,
                "title": record.title,
                "published": record.published,
                "created_at": record.created_at,
                "last_modified": record.last_modified,
                "cover_image": record.cover_image,
                "user": UserListReadSchema(
                    **{
                        "first_name": record.first_name,
                        "last_name": record.last_name,
                        "avatar": record.avatar,
                        "user_id": record.user_id,
                        "profession": record.profession,
                    }
                ),
            }
        )
        for record in guides
    ]
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


async def get_guide_by_id(db: Session, guide_id: int) -> Guide | None:
    guide: Guide = db.query(Guide).get(guide_id)
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


async def save_featured_image(file: UploadFile, db: Session, guide: Guide) -> Guide:
    """Check if cover image exists and create it if not. If it exists then do the update"""

    old_cover_image = guide.cover_image

    file_path = get_featured_image_upload_path(str(guide.guide_id), file.filename)
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


async def delete_featured_image(db: Session, guide: Guide) -> None:
    image = guide.cover_image

    if image and os.path.exists(image):
        os.remove(image)
    guide.cover_image = None
    db.add(guide)
    db.commit()
    return None


async def delete_guide(db: Session, guide: Guide) -> None:
    await delete_featured_image(db, guide)
    db.delete(guide)
    db.commit()
    return None
