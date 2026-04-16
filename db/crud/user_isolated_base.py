from typing import Any, Generic, Optional, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDUserIsolatedBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(
        self,
        db: AsyncSession,
        id: Any,
        user_id: int,
        include_deleted: bool = False,
    ) -> Optional[ModelType]:
        stmt = select(self.model).where(
            self.model.id == id,
            self.model.user_id == user_id,
        )
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ModelType]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        db: AsyncSession,
        obj_in: CreateSchemaType,
        user_id: int,
    ) -> ModelType:
        obj_in_data = obj_in.model_dump()
        obj_in_data["user_id"] = user_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        user_id: int,
    ) -> ModelType:
        if db_obj.user_id != user_id:
            return None
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def soft_delete(
        self,
        db: AsyncSession,
        id: Any,
        user_id: int,
    ) -> int:
        stmt = (
            update(self.model)
            .where(
                self.model.id == id,
                self.model.user_id == user_id,
            )
            .values(is_deleted=True)
            .execution_options(synchronize_session="fetch")
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    async def hard_delete(
        self,
        db: AsyncSession,
        id: Any,
        user_id: int,
    ) -> int:
        stmt = delete(self.model).where(
            self.model.id == id,
            self.model.user_id == user_id,
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount
