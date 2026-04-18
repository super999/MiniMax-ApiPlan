from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey, String, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class GenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationType(str, Enum):
    OUTLINE = "outline"
    CHARACTERS = "characters"
    CHAPTER = "chapter"
    CONTENT = "content"
    FULL_WORK = "full_work"


class GenerationRecord(Base):
    __tablename__ = "generation_records"

    generation_type: Mapped[GenerationType] = mapped_column(
        SQLEnum(GenerationType),
        index=True,
        nullable=False,
    )
    status: Mapped[GenerationStatus] = mapped_column(
        SQLEnum(GenerationStatus),
        default=GenerationStatus.PENDING,
        index=True,
        nullable=False,
    )
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, name="metadata")
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
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


class GenerationRecordBase(BaseModel):
    generation_type: GenerationType
    script_work_id: int


class GenerationRecordCreate(GenerationRecordBase):
    project_id: int
    script_chapter_id: Optional[int] = None
    prompt: Optional[str] = None
    model_used: Optional[str] = None
    metadata_: Optional[dict] = Field(default=None, alias="metadata")


class GenerationRecordUpdate(BaseModel):
    status: Optional[GenerationStatus] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class GenerationRecordResponse(GenerationRecordBase):
    id: int
    status: GenerationStatus
    script_chapter_id: Optional[int] = None
    prompt: Optional[str] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    metadata_: Optional[dict] = Field(default=None, alias="metadata")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    project_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True
