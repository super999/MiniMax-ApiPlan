from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.crud.base import CRUDBase
from db.models.chat_log import ChatLog, ChatLogCreate, ChatLogUpdate


class CRUDChatLog(CRUDBase[ChatLog, ChatLogCreate, ChatLogUpdate]):
    async def get_by_request_id(
        self,
        db: AsyncSession,
        request_id: str,
        include_deleted: bool = False,
    ) -> Optional[ChatLog]:
        stmt = select(self.model).where(self.model.request_id == request_id)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_model(
        self,
        db: AsyncSession,
        model_name: str,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ChatLog]:
        stmt = select(self.model).where(self.model.model_name == model_name)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_successful_logs(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ChatLog]:
        stmt = select(self.model).where(self.model.success == True)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())


chat_log_crud = CRUDChatLog(ChatLog)
