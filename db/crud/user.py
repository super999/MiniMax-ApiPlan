from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.crud.base import CRUDBase
from db.models.user import User, UserCreate, UserUpdate
from core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_username(
        self,
        db: AsyncSession,
        username: str,
        include_deleted: bool = False,
    ) -> Optional[User]:
        stmt = select(self.model).where(self.model.username == username)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str,
        include_deleted: bool = False,
    ) -> Optional[User]:
        stmt = select(self.model).where(self.model.email == email)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        obj_in_data = obj_in.model_dump()
        password = obj_in_data.pop("password")
        obj_in_data["hashed_password"] = get_password_hash(password)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_password(
        self,
        db: AsyncSession,
        db_obj: User,
        new_password: str,
    ) -> User:
        db_obj.hashed_password = get_password_hash(new_password)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(
        self,
        db: AsyncSession,
        username: str,
        password: str,
    ) -> Optional[User]:
        user = await self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user


user_crud = CRUDUser(User)
