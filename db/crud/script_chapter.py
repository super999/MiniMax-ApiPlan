from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.crud.user_isolated_base import CRUDUserIsolatedBase
from db.models.script_chapter import ScriptChapter, ScriptChapterCreate, ScriptChapterUpdate


class CRUDScriptChapter(CRUDUserIsolatedBase[ScriptChapter, ScriptChapterCreate, ScriptChapterUpdate]):
    async def get_by_script_work(
        self,
        db: AsyncSession,
        script_work_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ScriptChapter]:
        stmt = select(self.model).where(
            self.model.script_work_id == script_work_id,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.chapter_number.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_chapter_number(
        self,
        db: AsyncSession,
        script_work_id: int,
        chapter_number: int,
        user_id: int,
        include_deleted: bool = False,
    ) -> Optional[ScriptChapter]:
        stmt = select(self.model).where(
            self.model.script_work_id == script_work_id,
            self.model.chapter_number == chapter_number,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_max_chapter_number(
        self,
        db: AsyncSession,
        script_work_id: int,
        user_id: int,
        include_deleted: bool = False,
    ) -> int:
        stmt = select(self.model.chapter_number).where(
            self.model.script_work_id == script_work_id,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.order_by(self.model.chapter_number.desc()).limit(1)
        result = await db.execute(stmt)
        max_num = result.scalar_one_or_none()
        return max_num if max_num else 0

    async def update_content(
        self,
        db: AsyncSession,
        chapter_id: int,
        content: str,
        user_id: int,
    ) -> Optional[ScriptChapter]:
        chapter = await self.get_by_id(db, id=chapter_id, user_id=user_id)
        if not chapter:
            return None
        chapter.content = content
        await db.commit()
        await db.refresh(chapter)
        return chapter

    async def update_outline(
        self,
        db: AsyncSession,
        chapter_id: int,
        outline: str,
        user_id: int,
    ) -> Optional[ScriptChapter]:
        chapter = await self.get_by_id(db, id=chapter_id, user_id=user_id)
        if not chapter:
            return None
        chapter.outline = outline
        await db.commit()
        await db.refresh(chapter)
        return chapter

    async def update_status(
        self,
        db: AsyncSession,
        chapter_id: int,
        status: str,
        user_id: int,
    ) -> Optional[ScriptChapter]:
        chapter = await self.get_by_id(db, id=chapter_id, user_id=user_id)
        if not chapter:
            return None
        chapter.status = status
        await db.commit()
        await db.refresh(chapter)
        return chapter

    async def create(
        self,
        db: AsyncSession,
        obj_in: ScriptChapterCreate,
        user_id: int,
    ) -> ScriptChapter:
        obj_in_data = obj_in.model_dump()
        obj_in_data["user_id"] = user_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


script_chapter_crud = CRUDScriptChapter(ScriptChapter)
