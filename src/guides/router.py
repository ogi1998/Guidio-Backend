from fastapi import APIRouter, status, Query, Depends, UploadFile
from sqlalchemy.orm import Session

from auth.service import user_if_profile_is_active
from core.dependencies import DBDependency
from core.models import User, Guide
from guides import schemas, manager
from guides.constants import RetrieveOrder

router = APIRouter()


@router.get("",
            description="Get list of guides",
            status_code=status.HTTP_200_OK,
            response_model=schemas.GuideListReadSchema)
async def get_guides(db: Session = DBDependency,
                     order: RetrieveOrder = Query(default=RetrieveOrder.descending,
                                                  description="Retrieve order: asc/desc"),
                     page: int = Query(default=1, ge=1, description="Page to request"),
                     page_size: int = Query(default=50, ge=1, le=100,
                                            description="Page size")):
    return await manager.get_list_of_guides(db,
                                            page=page,
                                            page_size=page_size,
                                            order=order)


@router.post(path="",
             description="Create guide",
             status_code=status.HTTP_201_CREATED,
             response_model=schemas.GuideReadSchema)
async def create_guide(data: schemas.GuideCreateUpdateSchema,
                       db: Session = DBDependency,
                       user: User = Depends(user_if_profile_is_active)) -> Guide:
    guide: Guide = await manager.create_guide(db, user, data)
    return guide


@router.get(path="/cover_image",
            description="Get guide featured image",
            response_model=schemas.GuideCoverImageSchema,
            status_code=status.HTTP_200_OK)
async def get_featured_image(
        guide_id: int,
        db: Session = DBDependency,
        user: User = Depends(user_if_profile_is_active)):
    return await manager.get_guide_featured_image(db, guide_id, user)


@router.post(path="/cover_image",
             description="Set guide featured image",
             response_model=schemas.GuideCoverImageSchema,
             status_code=status.HTTP_201_CREATED)
async def save_featured_image(guide_id: int,
                              file: UploadFile,
                              db: Session = DBDependency,
                              user: User = Depends(user_if_profile_is_active)):
    return await manager.save_guide_featured_image(db, guide_id, user, file)


@router.put(path="/cover_image",
            description="Update guide featured image",
            response_model=schemas.GuideCoverImageSchema,
            status_code=status.HTTP_200_OK)
async def update_featured_image(guide_id: int,
                                file: UploadFile,
                                db: Session = DBDependency,
                                user: User = Depends(user_if_profile_is_active)):
    return await manager.save_guide_featured_image(db, guide_id, user, file)


@router.delete(path="/cover_image",
               description="Delete guide featured image",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_featured_image(guide_id: int,
                                db: Session = DBDependency,
                                user: User = Depends(user_if_profile_is_active)) -> None:
    return await manager.delete_guide_featured_image(guide_id, db, user)


@router.get(path="/search",
            description="Search guides by title",
            status_code=status.HTTP_200_OK,
            response_model=schemas.GuideListReadSchema)
async def get_guides_by_title(title: str,
                              page: int = Query(default=1, ge=1, description="Page to request"),
                              page_size: int = Query(default=50, ge=1, le=100,
                                                     description="Page size"),
                              db: Session = DBDependency):
    return await manager.get_guides_by_title(title, page, page_size, db)


@router.get(path="/{user_id}",
            description="Get guides by user ID",
            status_code=status.HTTP_200_OK,
            response_model=schemas.GuideListReadSchema)
async def get_guides_by_user_id(user_id: int,
                                page: int = Query(default=1, ge=1, description="Page to request"),
                                page_size: int = Query(default=50, ge=1, le=100,
                                                       description="Page size"),
                                db: Session = DBDependency,
                                user: User = Depends(user_if_profile_is_active)):
    return await manager.get_guides_by_user_id(user_id, page, page_size, db, user)


@router.get("/guide/{guide_id}",
            description="Get single guide by ID",
            status_code=status.HTTP_200_OK,
            response_model=schemas.GuideReadSchema)
async def get_guide_by_id(guide_id: int,
                          db: Session = DBDependency):
    return await manager.get_guide_by_id(guide_id, db)


@router.put(path="/{guide_id}",
            description="Update guide",
            status_code=status.HTTP_201_CREATED,
            response_model=schemas.GuideReadSchema)
async def update_guide(guide_id: int, data: schemas.GuideCreateUpdateSchema,
                       db: Session = DBDependency,
                       user: User = Depends(user_if_profile_is_active)):
    return await manager.update_guide(guide_id, data, db, user)


@router.delete(path="/{guide_id}",
               description="Delete guide",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_guide(guide_id: int,
                       db: Session = DBDependency,
                       user: User = Depends(user_if_profile_is_active)):
    return await manager.delete_guide(guide_id, db, user)
