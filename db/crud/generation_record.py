from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.crud.user_isolated_base import CRUDUserIsolatedBase
from db.models.generation_record import GenerationRecord, GenerationRecordCreate, GenerationRecordUpdate


class CRUDGenerationRecord(CRUDUserIsolatedBase[GenerationRecord, GenerationRecordCreate, GenerationRecordUpdate]):
    async def get_by_script_work(
        self,
        db: AsyncSession,
        script_work_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[GenerationRecord]:
        stmt = select(self.model).where(
            self.model.script_work_id == script_work_id,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_chapter(
        self,
        db: AsyncSession,
        script_chapter_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[GenerationRecord]:
        stmt = select(self.model).where(
            self.model.script_chapter_id == script_chapter_id,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_records(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[GenerationRecord]:
        from db.models.generation_record import GenerationStatus
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.status.in_([GenerationStatus.PENDING, GenerationStatus.PROCESSING]),
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        db: AsyncSession,
        record_id: int,
        status: str,
        user_id: int,
        result: Optional[str] = None,
        error_message: Optional[str] = None,
        tokens_used: Optional[int] = None,
    ) -> Optional[GenerationRecord]:
        record = await self.get_by_id(db, id=record_id, user_id=user_id)
        if not record:
            return None
        record.status = status
        if result is not None:
            record.result = result
        if error_message is not None:
            record.error_message = error_message
        if tokens_used is not None:
            record.tokens_used = tokens_used
        await db.commit()
        await db.refresh(record)
        return record

    async def create(
        self,
        db: AsyncSession,
        obj_in: GenerationRecordCreate,
        user_id: int,
    ) -> GenerationRecord:
        obj_in_data = obj_in.model_dump(by_alias=True)
        obj_in_data["user_id"] = user_id
        if "metadata" in obj_in_data:
            obj_in_data["metadata_"] = obj_in_data.pop("metadata")
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


generation_record_crud = CRUDGenerationRecord(GenerationRecord)
