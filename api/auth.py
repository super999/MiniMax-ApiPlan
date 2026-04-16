from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import get_logger
from core.security import create_access_token
from core.deps import get_current_user
from db.session import get_async_session
from db.crud.user import user_crud
from db.models.user import (
    User,
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_session),
) -> User:
    existing_user = await user_crud.get_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    
    if user_in.email:
        existing_email = await user_crud.get_by_email(db, email=user_in.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册",
            )
    
    user = await user_crud.create(db, obj_in=user_in)
    logger.info(f"用户注册成功: {user.username}")
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
)
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_async_session),
) -> Token:
    user = await user_crud.authenticate(
        db,
        username=user_in.username,
        password=user_in.password,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.id)
    logger.info(f"用户登录成功: {user.username}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


@router.post(
    "/logout",
    summary="用户退出登录",
)
async def logout(
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    logger.info(f"用户退出登录: {current_user.username}")
    return {"message": "退出成功"}
