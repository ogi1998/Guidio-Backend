from datetime import datetime

from pydantic import Field, field_validator

from core.schemas import BaseModelSchema
from users.schemas import UserReadSchema, UserListReadSchema


class GuideCoverImageSchema(BaseModelSchema):
    cover_image: str | None

    class Config:
        from_attributes = True


class GuideListSingleSchema(BaseModelSchema):
    guide_id: int
    title: str
    published: bool
    created_at: datetime
    last_modified: datetime
    cover_image: str | None
    user: UserListReadSchema

    class Config:
        from_attributes = True


class GuideListReadSchema(BaseModelSchema):
    pages: int
    guides: list[GuideListSingleSchema]


class GuideCreateUpdateSchema(BaseModelSchema):
    title: str = Field(min_length=1, max_length=70)
    content: str = Field(min_length=1)
    note: str | None = None
    published: bool

    @field_validator('title')
    def validate_title(cls, title: str):
        if len(title.strip()) == 0:
            raise ValueError('Title must not be empty')
        return title.strip()

    @field_validator('content')
    def validate_content(cls, content: str):
        if len(content.strip()) == 0:
            raise ValueError('Content must not be empty')
        return content.strip()

    @field_validator('note')
    def validate_note(cls, note: str | None):
        if note and len(note.strip()) == 0:
            raise ValueError('Note must not be empty')
        if not note:
            return None
        return note.strip()


class GuideReadSchema(GuideCreateUpdateSchema):
    guide_id: int
    created_at: datetime
    last_modified: datetime
    cover_image: str | None
    user: UserReadSchema

    class Config:
        from_attributes = True
