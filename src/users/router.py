from fastapi import APIRouter, Query, status, Depends, UploadFile, Response
from sqlalchemy.orm import Session

from auth.service import user_if_profile_is_active
from core.dependencies import DBDependency
from core.models import User
from core.settings import AUTH_TOKEN
from users import schemas, manager

router = APIRouter()


@router.get(path="/professions",
            description="Get professions based on search by name",
            response_model=list[schemas.ProfessionReadSchema])
async def get_profession_by_name(name: str,
                                 db: Session = DBDependency) -> list[schemas.ProfessionReadSchema]:
    professions = await manager.get_professions_by_name(name, db)
    return professions


@router.get(path="/instructors",
            description="Get list of users who are instructors",
            response_model=schemas.UserReadSchemaWithPages)
async def get_instructors(page: int = Query(default=1, ge=1, description="Page to request"),
                          page_size: int = Query(default=50, ge=1, le=100, description="Page size"),
                          db: Session = DBDependency) -> schemas.UserReadSchemaWithPages:
    return await manager.get_instructors(page, page_size, db)


@router.get(path="/instructors/search",
            status_code=status.HTTP_200_OK,
            description="Retrieve instructors via search",
            response_model=schemas.UserReadSchemaWithPages)
async def search_instructors(search: str,
                             page: int = Query(default=1, ge=1, description="Page to request"),
                             page_size: int = Query(default=50, ge=1, le=100,
                                                    description="Page size"),
                             db: Session = DBDependency):
    return await manager.search_instructors(search, page, page_size, db)


@router.get(path="/avatar",
            description="Get user avatar",
            response_model=schemas.UserAvatarSchema,
            status_code=status.HTTP_200_OK)
async def get_avatar(user: User = Depends(user_if_profile_is_active)):
    return await manager.get_user_avatar(user)


@router.post(path="/avatar",
             description="Save user avatar",
             response_model=schemas.UserReadSchema,
             status_code=status.HTTP_201_CREATED)
async def save_avatar(file: UploadFile, db: Session = DBDependency,
                      user: User = Depends(user_if_profile_is_active)):
    return await manager.save_user_avatar(file, db, user)


@router.put(path="/avatar",
            description="Update user avatar",
            response_model=schemas.UserReadSchema,
            status_code=status.HTTP_200_OK)
async def update_avatar(file: UploadFile, db: Session = DBDependency,
                        user: User = Depends(user_if_profile_is_active)):
    return await manager.save_user_avatar(file, db, user)


@router.delete(path="/avatar",
               description="Delete user avatar",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_avatar(db: Session = DBDependency,
                        user: User = Depends(user_if_profile_is_active)):
    return await manager.delete_user_avatar(db, user)


@router.get(path="/cover_image",
            description="Get user cover image",
            response_model=schemas.UserCoverImageSchema,
            status_code=status.HTTP_200_OK)
async def get_cover_image(user: User = Depends(user_if_profile_is_active)):
    return await manager.get_user_cover_image(user)


@router.post(path="/cover_image",
             description="Save user cover image",
             response_model=schemas.UserReadSchema,
             status_code=status.HTTP_201_CREATED)
async def save_cover_image(file: UploadFile, db: Session = DBDependency,
                           user: User = Depends(user_if_profile_is_active)):
    return await manager.save_user_cover_image(file, db, user)


@router.put(path="/cover_image",
            description="Update user cover image",
            response_model=schemas.UserReadSchema,
            status_code=status.HTTP_200_OK)
async def update_cover_image(file: UploadFile, db: Session = DBDependency,
                             user: User = Depends(user_if_profile_is_active)):
    return await manager.save_user_cover_image(file, db, user)


@router.delete(path="/cover_image",
               description="Delete user cover image",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_cover_image(db: Session = DBDependency,
                             user: User = Depends(user_if_profile_is_active)):
    return await manager.delete_user_cover_image(db, user)


@router.get(path="/{user_id}",
            description="Get user profile by id",
            response_model=schemas.UserReadSchema)
async def get_user_profile_by_id(user_id: int, db: Session = DBDependency):
    return await manager.get_user_profile_by_id(user_id, db)


@router.put(path='/{user_id}',
            description="Update user profile",
            response_model=schemas.UserReadSchema)
async def update_user_profile(user_id: int, data: schemas.UserProfileUpdateSchema,
                              db: Session = DBDependency,
                              user: User = Depends(user_if_profile_is_active)):
    return await manager.update_user_profile(user_id, data, db, user)


@router.delete(path='/{user_id}',
               description="Delete user profile",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile(user_id: int, response: Response, db: Session = DBDependency,
                              user: User = Depends(user_if_profile_is_active)):
    await manager.delete_user_profile(user_id, db, user)
    response.delete_cookie(AUTH_TOKEN)
    return None


@router.put(path="/{user_id}/update_password",
            description="Update user password",
            status_code=status.HTTP_200_OK,
            response_model=schemas.UserReadSchema)
async def update_user_password(user_id: int,
                               data: schemas.UserPasswordUpdateSchema,
                               db: Session = DBDependency,
                               user: User = Depends(user_if_profile_is_active)):
    return await manager.update_user_password(user_id, data, db, user)
