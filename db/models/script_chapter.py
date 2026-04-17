from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey, String, Text, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from db.models.script_work import ScriptWork


class ScriptChapterStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ScriptChapter(Base):
    __tablename__ = "script_chapters"

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    chapter_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    outline: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ScriptChapterStatus] = mapped_column(
        SQLEnum(ScriptChapterStatus),
        default=ScriptChapterStatus.DRAFT,
        index=True,
        nullable=False,
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

    script_work: Mapped["ScriptWork"] = relationship(
        "ScriptWork",
        back_populates="chapters",
    )


class ScriptChapterBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    chapter_number: int = Field(..., ge=1)


class ScriptChapterCreate(ScriptChapterBase):
    script_work_id: int
    project_id: int
    outline: Optional[str] = None
    content: Optional[str] = None


class ScriptChapterUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    chapter_number: Optional[int] = Field(default=None, ge=1)
    outline: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ScriptChapterStatus] = None


class ScriptChapterResponse(ScriptChapterBase):
    id: int
    outline: Optional[str] = None
    content: Optional[str] = None
    status: ScriptChapterStatus
    script_work_id: int
    project_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True
