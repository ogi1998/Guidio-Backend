from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session, Query

from core.models import Guide, User, Profession, UserDetail
from core.service import count_number_of_pages
from guides.constants import RetrieveOrder
from guides.schemas import GuideCreateUpdateSchema, GuideListSingleSchema, GuideListReadSchema
from users.schemas import UserListReadSchema


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


def get_initial_list_of_guides(db: Session,
                               search: str = '') -> Query | None:
    guides = db.query(
        Guide.guide_id,
        Guide.title,
        Guide.published,
        Guide.created_at,
        Guide.last_modified,
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


def get_list_of_guides(db: Session,
                       page: int,
                       page_size: int,
                       sort_order: str = RetrieveOrder.descending,
                       search: str = '',
                       published_only: bool = True) -> GuideListReadSchema | None:
    offset: int = page * page_size

    if sort_order == RetrieveOrder.descending:
        order_by_clause = desc(Guide.last_modified)
    else:
        order_by_clause = asc(Guide.last_modified)

    query = get_initial_list_of_guides(db, search=search)
    if published_only:
        guides = query.filter(Guide.published) \
            .order_by(order_by_clause)
    else:
        guides = query.order_by(order_by_clause)
    pages: int = count_number_of_pages(guides.count(), page_size)
    guides = guides.offset(offset).limit(page_size).all()
    guides_list: list[GuideListSingleSchema] = []
    for record in guides:
        guides_list.append(GuideListSingleSchema(
            guide_id=record[0],
            title=record[1],
            published=record[2],
            created_at=record[3],
            last_modified=record[4],
            user=UserListReadSchema(
                first_name=record[5],
                last_name=record[6],
                avatar=record[7],
                user_id=record[8],
                profession=record[9]
            )
        ))
    return GuideListReadSchema(pages=pages, guides=guides_list)


def search_guides(db: Session, title: str, page: int, page_size: int) -> GuideListReadSchema | None:
    guides = get_list_of_guides(db, page=page, page_size=page_size, search=title)
    return GuideListReadSchema(pages=guides.pages, guides=guides.guides)


def get_guides_by_user_id(db: Session,
                          user_id: int,
                          page: int,
                          page_size: int,
                          user: User):
    if user.user_id == user_id:
        guides = get_list_of_guides(db, page=page, page_size=page_size, published_only=False)
    else:
        guides = get_list_of_guides(db, page=page, page_size=page_size, published_only=True)
    return guides


def get_guide_by_id(db: Session, guide_id: int, user: User) -> Guide | None:
    guide: Guide = db.query(Guide).get(guide_id)
    if not guide:
        return None
    if not guide.user_id == user.user_id and not guide.published:
        return None
    return guide


def save_guide(db: Session,
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


def delete_guide(db: Session, guide_id: int) -> None:
    guide = db.query(Guide).get(guide_id)
    db.delete(guide)
    db.commit()
    return None
