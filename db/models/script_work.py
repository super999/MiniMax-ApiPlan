from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING, List
from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from db.models.script_chapter import ScriptChapter


class ScriptWorkStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ScriptWork(Base):
    __tablename__ = "script_works"

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outline: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    characters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ScriptWorkStatus] = mapped_column(
        SQLEnum(ScriptWorkStatus),
        default=ScriptWorkStatus.DRAFT,
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
    is_active: Mapped[bool] = mapped_column(default=True, index=True)

    chapters: Mapped[List["ScriptChapter"]] = relationship(
        "ScriptChapter",
        back_populates="script_work",
        cascade="all, delete-orphan",
    )


class ScriptWorkBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class ScriptWorkCreate(ScriptWorkBase):
    project_id: int
    outline: Optional[str] = None
    characters: Optional[str] = None


class ScriptWorkUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    outline: Optional[str] = None
    characters: Optional[str] = None
    status: Optional[ScriptWorkStatus] = None
    is_active: Optional[bool] = None


class ScriptWorkResponse(ScriptWorkBase):
    id: int
    outline: Optional[str] = None
    characters: Optional[str] = None
    status: ScriptWorkStatus
    project_id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True
