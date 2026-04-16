from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.crud.user_isolated_base import CRUDUserIsolatedBase
from db.models.project import Project, ProjectCreate, ProjectUpdate


class CRUDProject(CRUDUserIsolatedBase[Project, ProjectCreate, ProjectUpdate]):
    async def get_by_name(
        self,
        db: AsyncSession,
        name: str,
        user_id: int,
        include_deleted: bool = False,
    ) -> Optional[Project]:
        stmt = select(self.model).where(
            self.model.name == name,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_projects(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.is_active == True,
            self.model.is_deleted == False,
        )
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_name(
        self,
        db: AsyncSession,
        project_id: int,
        name: str,
        user_id: int,
    ) -> Optional[Project]:
        project = await self.get_by_id(db, id=project_id, user_id=user_id)
        if not project:
            return None
        project.name = name
        await db.commit()
        await db.refresh(project)
        return project


project_crud = CRUDProject(Project)
