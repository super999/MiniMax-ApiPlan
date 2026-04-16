from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import decode_access_token
from core.logger import get_logger
from db.session import get_async_session
from db.crud.user import user_crud
from db.models.user import User

logger = get_logger(__name__)

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if credentials is None:
        raise credentials_exception
    
    token = credentials.credentials
    user_id = decode_access_token(token)
    
    if user_id is None:
        raise credentials_exception
    
    user = await user_crud.get_by_id(db, id=user_id)
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    
    return user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_async_session),
) -> Optional[User]:
    if credentials is None:
        return None
    
    token = credentials.credentials
    user_id = decode_access_token(token)
    
    if user_id is None:
        return None
    
    user = await user_crud.get_by_id(db, id=user_id)
    
    if user is None or not user.is_active:
        return None
    
    return user
