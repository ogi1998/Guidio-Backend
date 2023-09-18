from fastapi import APIRouter, Depends, status, HTTPException, Query

from auth.dependencies import ValidToken
from auth.exceptions import invalid_credentials_exception
from auth.service import get_current_user
from core.dependencies import DBDependency
from core.models import User
from core.exceptions import non_existent_page_exception
from guides import schemas
from guides import service
from guides.constants import RetrieveOrder
from guides.exceptions import not_instructor_exception, guides_not_found_exception

router = APIRouter()


@router.get("",
            description="Get list of guides",
            status_code=status.HTTP_200_OK,
            response_model=schemas.GuideListReadSchema)
def get_list_of_guides(db=DBDependency,
                       order: RetrieveOrder = Query(default=RetrieveOrder.descending,
                                                    description="Retrieve order: asc/desc"),
                       page: int = Query(default=1, ge=1, description="Page to request"),
                       page_size: int = Query(default=50, ge=1, le=100, description="Page size")):
    total_pages = service.count_published_guides_pages(db, page_size)
    guides = service.get_list_of_guides(db,
                                        page=page - 1,
                                        page_size=page_size,
                                        sort_order=order,
                                        published_only=True)
    if not guides:
        raise guides_not_found_exception()
    if page > total_pages:
        raise non_existent_page_exception()
    return schemas.GuideListReadSchema(pages=total_pages, guides=guides)


@router.post(path="",
             dependencies=[ValidToken],
             description="Create guide",
             status_code=status.HTTP_201_CREATED,
             response_model=schemas.GuideReadSchema)
def create_guide(data: schemas.GuideCreateUpdateSchema,
                 db=DBDependency,
                 user: User = Depends(get_current_user)):
    if not user:
        raise invalid_credentials_exception()
    if not user.user_details.is_instructor:
        raise not_instructor_exception()
    guide = service.save_guide(db, data, user_id=user.user_id)
    return guide


@router.get(path="/search",
            dependencies=[ValidToken],
            description="Search guides by title",
            status_code=status.HTTP_200_OK,
            response_model=schemas.GuideListReadSchema)
def get_guides_by_title(title: str,
                        page: int = Query(default=1, ge=1, description="Page to request"),
                        page_size: int = Query(default=50, ge=1, le=100, description="Page size"),
                        db=DBDependency):
    total_pages = service.count_published_guides_pages(db, page_size)
    guides = service.search_guides(db, title, page=page-1, page_size=page_size)
    if not guides:
        raise guides_not_found_exception()
    if page > total_pages:
        raise non_existent_page_exception()
    return schemas.GuideListReadSchema(pages=total_pages, guides=guides)


@router.get(path="/{user_id}",
            dependencies=[ValidToken],
            description="Get guides by user ID",
            status_code=status.HTTP_200_OK,
            response_model=schemas.GuideListReadSchema)
def get_guides_by_user_id(user_id: int,
                          page: int = Query(default=1, ge=1, description="Page to request"),
                          page_size: int = Query(default=50, ge=1, le=100, description="Page size"),
                          db=DBDependency,
                          user: User = Depends(get_current_user)):
    if user.user_id == user_id:
        total_pages = service.count_pages(db, page_size)
    else:
        total_pages = service.count_published_guides_pages(db, page_size)
    guides = service.get_guides_by_user_id(db=db,
                                           user_id=user_id,
                                           page=page - 1,
                                           page_size=page_size,
                                           user=user)
    if not guides:
        raise guides_not_found_exception()
    if page > total_pages:
        raise non_existent_page_exception()
    return schemas.GuideListReadSchema(pages=total_pages, guides=guides)


@router.get("/guide/{guide_id}",
            dependencies=[ValidToken],
            description="Get single guide by ID",
            status_code=status.HTTP_200_OK,
            response_model=schemas.GuideReadSchema)
def get_guide_by_id(guide_id: int,
                    db=DBDependency,
                    user: User = Depends(get_current_user)):
    guide = service.get_guide_by_id(db, guide_id, user)
    if not guide:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide not found")
    return guide


@router.put(path="/{guide_id}",
            dependencies=[ValidToken],
            description="Update guide",
            status_code=status.HTTP_201_CREATED,
            response_model=schemas.GuideReadSchema)
def update_guide(guide_id: int, data: schemas.GuideCreateUpdateSchema,
                 db=DBDependency,
                 user: User = Depends(get_current_user)):
    guide = service.get_guide_by_id(db, guide_id, user)
    if not guide:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide not found")
    if not user.user_details.is_instructor:
        raise not_instructor_exception()
    return service.save_guide(db, data, user_id=user.user_id, guide=guide)


@router.delete(path="/{guide_id}",
               dependencies=[ValidToken],
               description="Delete guide",
               status_code=status.HTTP_204_NO_CONTENT)
def delete_guide(guide_id: int,
                 db=DBDependency,
                 user: User = Depends(get_current_user)):
    guide = service.get_guide_by_id(db, guide_id, user)
    if not guide:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide not found")
    if user.user_id != guide.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return service.delete_guide(db, guide_id)
