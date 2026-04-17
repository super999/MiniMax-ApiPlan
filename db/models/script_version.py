from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class ScriptVersion(Base):
    __tablename__ = "script_versions"

    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    outline: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    characters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    change_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    script_chapter_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("script_chapters.id"),
        index=True,
        nullable=True,
    )
    script_work_id: Mapped[int] = mapped_column(
        ForeignKey("script_works.id"),
        index=True,
        nullable=False,
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )


class ScriptVersionBase(BaseModel):
    version_number: int = Field(..., ge=1)
    change_log: Optional[str] = Field(default=None, max_length=500)


class ScriptVersionCreate(ScriptVersionBase):
    script_work_id: int
    script_chapter_id: Optional[int] = None
    title: Optional[str] = Field(default=None, max_length=200)
    outline: Optional[str] = None
    content: Optional[str] = None
    characters: Optional[str] = None
    description: Optional[str] = None


class ScriptVersionResponse(ScriptVersionBase):
    id: int
    script_chapter_id: Optional[int] = None
    script_work_id: int
    project_id: int
    user_id: int
    title: Optional[str] = None
    outline: Optional[str] = None
    content: Optional[str] = None
    characters: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True
