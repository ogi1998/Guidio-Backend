from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text, ForeignKey
from sqlalchemy.orm import relationship

from core.constants import ACTIVATE_ACCOUNT_SUBJECT
from src.database import Base
from utils.mail.send_mail import send_mail


# CODEBOOKS
class Profession(Base):
    __tablename__ = "profession"

    profession_id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    user_details = relationship("UserDetail", back_populates="profession")


# USERS
class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_details = relationship("UserDetail",
                                back_populates="user",
                                uselist=False,
                                cascade="all, delete",
                                passive_deletes=True)
    guides = relationship("Guide",
                          back_populates="user",
                          cascade="all, delete",
                          passive_deletes=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    async def email_user(self, subject: str, body: Dict[str, Any], template_name: str):
        """Send email to this user."""
        await send_mail(subject=subject, recipients=[self.email], body=body,
                        template_name=template_name)


class UserDetail(Base):
    __tablename__ = "user_detail"

    def __init__(self, user_id: int, profession_id=None, bio="", linkedin="", github="", website="",
                 is_instructor=False, avatar=None, cover_image=None, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.profession_id = profession_id
        self.bio = bio
        self.linkedin = linkedin
        self.github = github
        self.website = website
        self.is_instructor = is_instructor
        self.avatar = avatar
        self.cover_image = cover_image

    user_detail_id = Column(Integer, primary_key=True)
    profession_id = Column(Integer, ForeignKey('profession.profession_id', ondelete="SET NULL"),
                           nullable=True)
    bio = Column(String(255))
    linkedin = Column(String(255))
    github = Column(String(255))
    website = Column(String(255))
    is_instructor = Column(Boolean, default=False, nullable=False)
    avatar = Column(String(255), nullable=True)
    cover_image = Column(String(255), nullable=True)

    user_id = Column(Integer, ForeignKey('user.user_id', ondelete="CASCADE"), unique=True)
    user = relationship("User", back_populates="user_details")
    profession = relationship("Profession", back_populates="user_details")


# GUIDES
class Guide(Base):
    __tablename__ = "guide"

    guide_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(70), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_modified = Column(DateTime(timezone=True), server_default=func.now(),
                           onupdate=func.current_timestamp(), nullable=False)
    published = Column(Boolean, default=False, nullable=False)
    note = Column(String(255), nullable=True)
    cover_image = Column(String(255), nullable=True)

    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"))

    user = relationship("User", back_populates="guides")

    def __str__(self):
        return self.title
