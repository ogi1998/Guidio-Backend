from fastapi import APIRouter, Depends, status, HTTPException, Response, UploadFile, Query

from auth.exceptions import invalid_credentials_exception
from auth.service import get_current_active_user, verify_password
from core.dependencies import DBDependency
from core.exceptions import non_existent_page_exception
from core.models import User
from core.settings import AUTH_TOKEN
from users import service, schemas

router = APIRouter()


@router.get(path="/professions",
            description="Get professions based on search by name",
            response_model=list[schemas.ProfessionReadSchema])
async def get_profession_by_name(name: str,
                                 db=DBDependency):
    professions = await service.get_professions_by_name(db, name)
    return professions


@router.get(path="/instructors",
            description="Get list of users who are instructors",
            response_model=schemas.UserReadSchemaWithPages)
async def get_instructors(page: int = Query(default=1, ge=1, description="Page to request"),
                          page_size: int = Query(default=50, ge=1, le=100, description="Page size"),
                          db=DBDependency) -> schemas.UserReadSchemaWithPages:
    instructors = await service.get_paginated_instructors(db, page - 1, page_size)
    if page > instructors.pages:
        raise non_existent_page_exception()
    return instructors


@router.get(path="/instructors/search",
            status_code=status.HTTP_200_OK,
            description="Retrieve instructors via search",
            response_model=schemas.UserReadSchemaWithPages)
async def search_instructors(search: str,
                             page: int = Query(default=1, ge=1, description="Page to request"),
                             page_size: int = Query(default=50, ge=1, le=100,
                                                    description="Page size"),
                             db=DBDependency):
    total_pages = await service.get_number_of_instructors_from_search(db, search, page_size)
    if page > total_pages:
        raise non_existent_page_exception()
    instructors = await service.get_paginated_instructors_by_search(db, page=page - 1,
                                                                    page_size=page_size,
                                                                    search=search)
    return schemas.UserReadSchemaWithPages(pages=total_pages, users=instructors)


@router.get(path="/avatar",
            description="Get user avatar",
            response_model=schemas.UserAvatarSchema,
            status_code=status.HTTP_200_OK)
async def get_avatar(user: User = Depends(get_current_active_user)):
    avatar = await service.get_avatar(user)
    if avatar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Avatar not found")
    return schemas.UserAvatarSchema(avatar=avatar)


@router.post(path="/avatar",
             description="Create user avatar",
             response_model=schemas.UserReadSchema,
             status_code=status.HTTP_201_CREATED)
async def create_avatar(file: UploadFile, db=DBDependency,
                        user: User = Depends(get_current_active_user)):
    saved = await service.save_avatar(file, db, user)
    return saved


@router.put(path="/avatar",
            description="Update user avatar",
            response_model=schemas.UserReadSchema,
            status_code=status.HTTP_200_OK)
async def update_avatar(file: UploadFile, db=DBDependency,
                        user: User = Depends(get_current_active_user)):
    updated = await service.save_avatar(file, db, user)
    return updated


@router.delete(path="/avatar",
               description="Delete user avatar",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_avatar(db=DBDependency, user: User = Depends(get_current_active_user)):
    avatar = user.user_details.avatar
    if avatar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Avatar not found")
    await service.delete_avatar(db, user)
    return None


@router.get(path="/cover_image",
            description="Get user cover image",
            response_model=schemas.UserCoverImageSchema,
            status_code=status.HTTP_200_OK)
async def get_cover_image(user: User = Depends(get_current_active_user)):
    image = await service.get_cover_image(user)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Cover image not found")
    return schemas.UserCoverImageSchema(cover_image=image)


@router.post(path="/cover_image",
             description="Create user cover image",
             response_model=schemas.UserReadSchema,
             status_code=status.HTTP_201_CREATED)
async def create_cover_image(file: UploadFile, db=DBDependency,
                             user: User = Depends(get_current_active_user)):
    saved = await service.save_cover_image(file, db, user)
    return saved


@router.put(path="/cover_image",
            description="Update user cover image",
            response_model=schemas.UserReadSchema,
            status_code=status.HTTP_200_OK)
async def update_cover_image(file: UploadFile, db=DBDependency,
                             user: User = Depends(get_current_active_user)):
    updated = await service.save_cover_image(file, db, user)
    return updated


@router.delete(path="/cover_image",
               description="Delete user cover image",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_cover_image(db=DBDependency, user: User = Depends(get_current_active_user)):
    image = user.user_details.cover_image
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Cover image not found")
    await service.delete_cover_image(db, user)
    return None


@router.get(path="/{user_id}",
            description="Get user profile by id",
            response_model=schemas.UserReadSchema)
async def get_user_profile_by_id(user_id: int, db=DBDependency):
    user = await service.get_user_profile_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put(path='/{user_id}',
            description="Update user profile",
            response_model=schemas.UserReadSchema)
async def update_user_profile(user_id: int, data: schemas.UserProfileUpdateSchema, db=DBDependency,
                              user: User = Depends(get_current_active_user)):
    if user_id != user.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if data.user_details.profession_id:
        profession = await service.get_profession_by_id(db, data.user_details.profession_id)
        if not profession:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Profession doesn't exist")
    await service.update_user_profile(data, db, user)
    return user


@router.delete(path='/{user_id}',
               description="Delete user profile",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile(user_id: int, response: Response, db=DBDependency,
                              user: User = Depends(get_current_active_user)):
    if not user or user_id != user.user_id:
        raise await invalid_credentials_exception()
    response.delete_cookie(AUTH_TOKEN)
    return await service.delete_user_profile(db, user_id)


@router.put(path="/{user_id}/update_password",
            description="Update user password",
            status_code=status.HTTP_200_OK,
            response_model=schemas.UserReadSchema)
async def update_user_password(user_id: int,
                               data: schemas.UserPasswordUpdateSchema,
                               db=DBDependency,
                               user: User = Depends(get_current_active_user)):
    if user_id != user.user_id:
        raise await invalid_credentials_exception()
    if not await verify_password(data.current_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid password")
    updated_user = await service.update_user_password(db, data, user)
    return updated_user
