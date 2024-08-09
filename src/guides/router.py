from fastapi import APIRouter, Depends, status, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from auth.exceptions import InvalidCredentialsException
from auth import service as auth_service
from core.dependencies import get_db
from core.exceptions import PageNotFoundException
from core.models import User
from guides import schemas
from guides import service
from guides.constants import RetrieveOrder
from guides.exceptions import GuidesNotFoundException, NotInstructorException
# from utils.auth import is_profile_active, get_user_from_token

router = APIRouter()


# @router.get("",
#             description="Get list of guides",
#             status_code=status.HTTP_200_OK,
#             response_model=schemas.GuideListReadSchema)
# async def get_list_of_guides(db: Session = Depends(get_db),
#                              order: RetrieveOrder = Query(default=RetrieveOrder.descending,
#                                                           description="Retrieve order: asc/desc"),
#                              page: int = Query(default=1, ge=1, description="Page to request"),
#                              page_size: int = Query(default=50, ge=1, le=100,
#                                                     description="Page size")):
#     guides = await service.get_list_of_guides(db,
#                                               page=page - 1,
#                                               page_size=page_size,
#                                               sort_order=order,
#                                               published_only=True)
#     if not guides.guides:
#         raise GuidesNotFoundException()
#     if page > guides.pages:
#         raise PageNotFoundException()
#     return schemas.GuideListReadSchema(pages=guides.pages, guides=guides.guides)
#
#
# @router.post(path="",
#              description="Create guide",
#              dependencies=[Depends(is_profile_active)],
#              status_code=status.HTTP_201_CREATED,
#              response_model=schemas.GuideReadSchema)
# async def create_guide(data: schemas.GuideCreateUpdateSchema,
#                        db: Session = Depends(get_db),
#                        user: User = Depends(get_user_from_token)):
#     if not user:
#         raise InvalidCredentialsException()
#     if not user.user_details.is_instructor:
#         raise NotInstructorException()
#     prepared_data = await service.prepare_guide_data(data)
#     guide = await service.save_guide(db, prepared_data, user_id=user.user_id)
#     return guide
#
#
# @router.get(path="/cover_image",
#             description="Get guide cover image",
#             dependencies=[Depends(is_profile_active)],
#             response_model=schemas.GuideCoverImageSchema,
#             status_code=status.HTTP_200_OK)
# async def get_cover_image(guide_id: int,
#                           user: User = Depends(get_user_from_token),
#                           db: Session = Depends(get_db)):
#     guide = await service.get_guide_by_id(db, guide_id, user)
#     if not guide:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide not found")
#     image = await service.get_cover_image(guide)
#     if image is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail="Cover image not found")
#     return schemas.GuideCoverImageSchema(cover_image=image)
#
#
# @router.post(path="/cover_image",
#              description="Create guide cover image",
#              dependencies=[Depends(is_profile_active)],
#              response_model=schemas.GuideCoverImageSchema,
#              status_code=status.HTTP_201_CREATED)
# async def create_cover_image(guide_id: int,
#                              file: UploadFile,
#                              db: Session = Depends(get_db),
#                              user: User = Depends(get_user_from_token)):
#     guide = await service.get_guide_by_id(db, guide_id, user)
#     if not guide:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide not found")
#     if user.user_id != guide.user_id:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
#     saved = await service.save_cover_image(file, db, guide)
#     return saved
#
#
# @router.put(path="/cover_image",
#             description="Update guide cover image",
#             dependencies=[Depends(is_profile_active)],
#             response_model=schemas.GuideCoverImageSchema,
#             status_code=status.HTTP_200_OK)
# async def update_cover_image(guide_id: int,
#                              file: UploadFile,
#                              db: Session = Depends(get_db),
#                              user: User = Depends(get_user_from_token)):
#     guide = await service.get_guide_by_id(db, guide_id, user)
#     if not guide:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide not found")
#     if user.user_id != guide.user_id:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
#     updated = await service.save_cover_image(file, db, guide)
#     return updated
#
#
# @router.delete(path="/cover_image",
#                description="Delete user cover image",
#                dependencies=[Depends(is_profile_active)],
#                status_code=status.HTTP_204_NO_CONTENT)
# async def delete_cover_image(guide_id: int,
#                              db: Session = Depends(get_db),
#                              user: User = Depends(get_user_from_token)):
#     guide = await service.get_guide_by_id(db, guide_id, user)
#     if not guide:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide not found")
#     if user.user_id != guide.user_id:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
#     image = guide.cover_image
#     if image is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail="Cover image not found")
#     await service.delete_cover_image(db, guide)
#     return None
#
#
# @router.get(path="/search",
#             description="Search guides by title",
#             status_code=status.HTTP_200_OK,
#             response_model=schemas.GuideListReadSchema)
# async def get_guides_by_title(title: str,
#                               page: int = Query(default=1, ge=1, description="Page to request"),
#                               page_size: int = Query(default=50, ge=1, le=100,
#                                                      description="Page size"),
#                               db: Session = Depends(get_db)):
#     guides = await service.search_guides(db, title, page=page - 1, page_size=page_size)
#     if not guides.guides:
#         raise GuidesNotFoundException()
#     if page > guides.pages:
#         raise PageNotFoundException()
#     return guides
#
#
# @router.get(path="/{user_id}",
#             description="Get guides by user ID",
#             status_code=status.HTTP_200_OK,
#             dependencies=[Depends(is_profile_active)],
#             response_model=schemas.GuideListReadSchema)
# async def get_guides_by_user_id(user_id: int,
#                                 page: int = Query(default=1, ge=1, description="Page to request"),
#                                 page_size: int = Query(default=50, ge=1, le=100,
#                                                        description="Page size"),
#                                 db: Session = Depends(get_db),
#                                 user: User = Depends(get_user_from_token)):
#     guides = await service.get_guides_by_user_id(db=db,
#                                                  user_id=user_id,
#                                                  page=page - 1,
#                                                  page_size=page_size,
#                                                  user=user)
#     if not guides.guides:
#         raise GuidesNotFoundException()
#     if page > guides.pages:
#         raise PageNotFoundException()
#     return schemas.GuideListReadSchema(pages=guides.pages, guides=guides.guides)
#
#
# @router.get("/guide/{guide_id}",
#             description="Get single guide by ID",
#             status_code=status.HTTP_200_OK,
#             dependencies=[Depends(is_profile_active)],
#             response_model=schemas.GuideReadSchema)
# async def get_guide_by_id(guide_id: int,
#                           db: Session = Depends(get_db),
#                           user: User = Depends(get_user_from_token)):
#     guide = await service.get_guide_by_id(db, guide_id, user)
#     if not guide:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide not found")
#     return guide
#
#
# @router.put(path="/{guide_id}",
#             description="Update guide",
#             status_code=status.HTTP_201_CREATED,
#             dependencies=[Depends(is_profile_active)],
#             response_model=schemas.GuideReadSchema)
# async def update_guide(guide_id: int, data: schemas.GuideCreateUpdateSchema,
#                        db: Session = Depends(get_db),
#                        user: User = Depends(get_user_from_token)):
#     guide = await service.get_guide_by_id(db, guide_id, user)
#     if not guide:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide not found")
#     if not user.user_details.is_instructor:
#         raise NotInstructorException()
#     prepared_data = await service.prepare_guide_data(data)
#     return await service.save_guide(db, prepared_data, user_id=user.user_id, guide=guide)
#
#
# @router.delete(path="/{guide_id}",
#                description="Delete guide",
#                dependencies=[Depends(is_profile_active)],
#                status_code=status.HTTP_204_NO_CONTENT)
# async def delete_guide(guide_id: int,
#                        db: Session = Depends(get_db),
#                        user: User = Depends(get_user_from_token)):
#     guide = await service.get_guide_by_id(db, guide_id, user)
#     if not guide:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide not found")
#     if user.user_id != guide.user_id:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
#     return await service.delete_guide(db, guide)
