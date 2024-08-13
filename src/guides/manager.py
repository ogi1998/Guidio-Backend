from fastapi import UploadFile
from sqlalchemy.orm import Session

from auth.exceptions import InvalidCredentialsException, UnauthorizedException
from core.exceptions import ImageNotFoundException
from core.models import User, Guide
from guides import service, schemas
from guides.exceptions import GuidesNotFoundException, NotInstructorException, \
    GuideNotFoundException


async def get_list_of_guides(db: Session, page: int, page_size: int,
                             order: str) -> schemas.GuideListReadSchema:
    guides = await service.get_list_of_guides(db,
                                              page=page - 1,
                                              page_size=page_size,
                                              sort_order=order,
                                              published_only=True)
    if not guides.guides:
        raise GuidesNotFoundException()
    return schemas.GuideListReadSchema(pages=guides.pages, guides=guides.guides)


async def create_guide(db: Session, user: User, data: schemas.GuideCreateUpdateSchema) -> Guide:
    if not user:
        raise InvalidCredentialsException()
    if not user.user_details.is_instructor:
        raise NotInstructorException()
    guide = await service.save_guide(db, data, user_id=user.user_id)
    return guide


async def get_guide_featured_image(db: Session, guide_id: int,
                                   user: User) -> schemas.GuideCoverImageSchema:
    guide: Guide = await service.get_guide_by_id(db, guide_id)
    if not guide:
        raise GuideNotFoundException()
    elif not guide.user_id == user.user_id and not guide.published:
        raise UnauthorizedException()
    elif guide.cover_image is None:
        raise ImageNotFoundException()
    return schemas.GuideCoverImageSchema(cover_image=guide.cover_image)


async def save_guide_featured_image(db: Session, guide_id: int, user: User,
                                    file: UploadFile) -> schemas.GuideCoverImageSchema:
    guide: Guide = await service.get_guide_by_id(db, guide_id)
    if not guide:
        raise GuideNotFoundException()
    elif not guide.user_id == user.user_id:
        raise UnauthorizedException()
    saved = await service.save_featured_image(file, db, guide)
    return saved


async def delete_guide_featured_image(guide_id: int, db: Session, user: User) -> None:
    guide = await service.get_guide_by_id(db, guide_id)
    if not guide:
        raise GuideNotFoundException()
    elif not guide.user_id == user.user_id:
        raise UnauthorizedException()
    elif guide.cover_image is None:
        raise ImageNotFoundException()
    await service.delete_featured_image(db, guide)
    return None


async def get_guides_by_title(title: str, page: int, page_size: int,
                              db: Session) -> schemas.GuideListReadSchema:
    guides = await service.search_guides(db, title, page=page - 1, page_size=page_size)
    if not guides.guides:
        raise GuidesNotFoundException()
    return guides


async def get_guides_by_user_id(user_id: int, page: int, page_size: int, db: Session,
                                user: User) -> schemas.GuideListReadSchema:
    guides = await service.get_guides_by_user_id(db=db,
                                                 user_id=user_id,
                                                 page=page - 1,
                                                 page_size=page_size,
                                                 user=user)
    if not guides.guides:
        raise GuidesNotFoundException()
    return schemas.GuideListReadSchema(pages=guides.pages, guides=guides.guides)


async def get_guide_by_id(guide_id: int, db: Session) -> schemas.GuideReadSchema:
    guide = await service.get_guide_by_id(db, guide_id)
    if not guide:
        raise GuideNotFoundException()
    return guide


async def update_guide(guide_id: int, data: schemas.GuideCreateUpdateSchema, db: Session,
                       user: User):
    guide = await service.get_guide_by_id(db, guide_id)
    if not guide:
        raise GuideNotFoundException()
    elif not guide.user_id == user.user_id:
        raise UnauthorizedException()
    elif not user.user_details.is_instructor:
        raise NotInstructorException()
    return await service.save_guide(db, data, user_id=user.user_id, guide=guide)


async def delete_guide(guide_id: int, db: Session, user: User):
    guide = await service.get_guide_by_id(db, guide_id)
    if not guide:
        raise GuideNotFoundException()
    elif not guide.user_id == user.user_id:
        raise UnauthorizedException()
    return await service.delete_guide(db, guide)
