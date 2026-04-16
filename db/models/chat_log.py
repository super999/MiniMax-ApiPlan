from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class ChatLog(Base):
    __tablename__ = "chat_logs"

    request_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    temperature: Mapped[Optional[float]] = mapped_column(nullable=True)
    max_tokens: Mapped[Optional[int]] = mapped_column(nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[Optional[float]] = mapped_column(nullable=True)
    success: Mapped[Optional[bool]] = mapped_column(default=False, index=True)
    error_msg: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class ChatLogBase(BaseModel):
    request_id: Optional[str] = Field(default=None, max_length=100)
    model_name: Optional[str] = Field(default=None, max_length=100)
    prompt: str = Field(..., min_length=1)
    response: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    latency_ms: Optional[float] = None
    success: Optional[bool] = None
    error_msg: Optional[str] = None
    meta_data: Optional[dict] = None


class ChatLogCreate(ChatLogBase):
    pass


class ChatLogUpdate(ChatLogBase):
    pass


class ChatLogResponse(ChatLogBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True
