from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.crud.user_isolated_base import CRUDUserIsolatedBase
from db.models.script_version import ScriptVersion, ScriptVersionCreate, ScriptVersionUpdate


class CRUDScriptVersion(CRUDUserIsolatedBase[ScriptVersion, ScriptVersionCreate, ScriptVersionUpdate]):
    async def get_by_script_work(
        self,
        db: AsyncSession,
        script_work_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ScriptVersion]:
        stmt = select(self.model).where(
            self.model.script_work_id == script_work_id,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.version_number.desc())
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
    ) -> list[ScriptVersion]:
        stmt = select(self.model).where(
            self.model.script_chapter_id == script_chapter_id,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.version_number.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_version(
        self,
        db: AsyncSession,
        script_work_id: int,
        user_id: int,
        script_chapter_id: Optional[int] = None,
        include_deleted: bool = False,
    ) -> Optional[ScriptVersion]:
        stmt = select(self.model).where(
            self.model.script_work_id == script_work_id,
            self.model.user_id == user_id,
        )
        if script_chapter_id is not None:
            stmt = stmt.where(self.model.script_chapter_id == script_chapter_id)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.order_by(self.model.version_number.desc()).limit(1)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_max_version_number(
        self,
        db: AsyncSession,
        script_work_id: int,
        user_id: int,
        script_chapter_id: Optional[int] = None,
        include_deleted: bool = False,
    ) -> int:
        stmt = select(self.model.version_number).where(
            self.model.script_work_id == script_work_id,
            self.model.user_id == user_id,
        )
        if script_chapter_id is not None:
            stmt = stmt.where(self.model.script_chapter_id == script_chapter_id)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.order_by(self.model.version_number.desc()).limit(1)
        result = await db.execute(stmt)
        max_num = result.scalar_one_or_none()
        return max_num if max_num else 0

    async def create(
        self,
        db: AsyncSession,
        obj_in: ScriptVersionCreate,
        user_id: int,
    ) -> ScriptVersion:
        obj_in_data = obj_in.model_dump()
        obj_in_data["user_id"] = user_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


script_version_crud = CRUDScriptVersion(ScriptVersion)
