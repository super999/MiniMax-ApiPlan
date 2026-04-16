from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.crud.user_isolated_base import CRUDUserIsolatedBase
from db.models.chat_log import ChatLog, ChatLogCreate, ChatLogUpdate


class CRUDChatLog(CRUDUserIsolatedBase[ChatLog, ChatLogCreate, ChatLogUpdate]):
    async def get_by_request_id(
        self,
        db: AsyncSession,
        request_id: str,
        user_id: int,
        project_id: Optional[int] = None,
        include_deleted: bool = False,
    ) -> Optional[ChatLog]:
        stmt = select(self.model).where(
            self.model.request_id == request_id,
            self.model.user_id == user_id,
        )
        if project_id is not None:
            stmt = stmt.where(self.model.project_id == project_id)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_model(
        self,
        db: AsyncSession,
        model_name: str,
        user_id: int,
        project_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ChatLog]:
        stmt = select(self.model).where(
            self.model.model_name == model_name,
            self.model.user_id == user_id,
        )
        if project_id is not None:
            stmt = stmt.where(self.model.project_id == project_id)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_successful_logs(
        self,
        db: AsyncSession,
        user_id: int,
        project_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ChatLog]:
        stmt = select(self.model).where(
            self.model.success == True,
            self.model.user_id == user_id,
        )
        if project_id is not None:
            stmt = stmt.where(self.model.project_id == project_id)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_project(
        self,
        db: AsyncSession,
        project_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ChatLog]:
        stmt = select(self.model).where(
            self.model.project_id == project_id,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())


chat_log_crud = CRUDChatLog(ChatLog)
