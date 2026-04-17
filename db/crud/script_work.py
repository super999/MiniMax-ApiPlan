from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.crud.user_isolated_base import CRUDUserIsolatedBase
from db.models.script_work import ScriptWork, ScriptWorkCreate, ScriptWorkUpdate
from db.models.script_chapter import ScriptChapter


class CRUDScriptWork(CRUDUserIsolatedBase[ScriptWork, ScriptWorkCreate, ScriptWorkUpdate]):
    async def get_by_id_with_chapters(
        self,
        db: AsyncSession,
        id: int,
        user_id: int,
        include_deleted: bool = False,
    ) -> Optional[ScriptWork]:
        stmt = select(self.model).options(
            selectinload(self.model.chapters)
        ).where(
            self.model.id == id,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        db: AsyncSession,
        project_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ScriptWork]:
        stmt = select(self.model).where(
            self.model.project_id == project_id,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_title(
        self,
        db: AsyncSession,
        title: str,
        project_id: int,
        user_id: int,
        include_deleted: bool = False,
    ) -> Optional[ScriptWork]:
        stmt = select(self.model).where(
            self.model.title == title,
            self.model.project_id == project_id,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_outline(
        self,
        db: AsyncSession,
        script_work_id: int,
        outline: str,
        user_id: int,
    ) -> Optional[ScriptWork]:
        script_work = await self.get_by_id(db, id=script_work_id, user_id=user_id)
        if not script_work:
            return None
        script_work.outline = outline
        await db.commit()
        await db.refresh(script_work)
        return script_work

    async def update_characters(
        self,
        db: AsyncSession,
        script_work_id: int,
        characters: str,
        user_id: int,
    ) -> Optional[ScriptWork]:
        script_work = await self.get_by_id(db, id=script_work_id, user_id=user_id)
        if not script_work:
            return None
        script_work.characters = characters
        await db.commit()
        await db.refresh(script_work)
        return script_work

    async def update_status(
        self,
        db: AsyncSession,
        script_work_id: int,
        status: str,
        user_id: int,
    ) -> Optional[ScriptWork]:
        script_work = await self.get_by_id(db, id=script_work_id, user_id=user_id)
        if not script_work:
            return None
        script_work.status = status
        await db.commit()
        await db.refresh(script_work)
        return script_work

    async def create(
        self,
        db: AsyncSession,
        obj_in: ScriptWorkCreate,
        user_id: int,
    ) -> ScriptWork:
        obj_in_data = obj_in.model_dump()
        obj_in_data["user_id"] = user_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


script_work_crud = CRUDScriptWork(ScriptWork)
