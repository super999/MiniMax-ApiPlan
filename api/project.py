from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import get_logger
from core.deps import get_current_user
from db.session import get_async_session
from db.crud.project import project_crud
from db.models.user import User
from db.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建项目",
    responses={
        201: {"description": "项目创建成功"},
        400: {"description": "项目名称已存在"},
        401: {"description": "未授权，请先登录"},
    },
)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Project:
    existing_project = await project_crud.get_by_name(
        db,
        name=project_in.name,
        user_id=current_user.id,
    )
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"项目名称 '{project_in.name}' 已存在",
        )

    project = await project_crud.create(
        db,
        obj_in=project_in,
        user_id=current_user.id,
    )
    logger.info(f"用户 {current_user.username} 创建了项目: {project.name}")
    return project


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="获取用户的所有项目",
    responses={
        200: {"description": "获取成功"},
        401: {"description": "未授权，请先登录"},
    },
)
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> list[Project]:
    projects = await project_crud.get_multi(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return projects


@router.get(
    "/active",
    response_model=list[ProjectResponse],
    summary="获取用户的所有活跃项目",
    responses={
        200: {"description": "获取成功"},
        401: {"description": "未授权，请先登录"},
    },
)
async def get_active_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> list[Project]:
    projects = await project_crud.get_active_projects(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return projects


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="获取单个项目详情",
    responses={
        200: {"description": "获取成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "项目不存在或无权限访问"},
    },
)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Project:
    project = await project_crud.get_by_id(
        db,
        id=project_id,
        user_id=current_user.id,
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在或无权限访问",
        )
    return project


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="更新项目",
    responses={
        200: {"description": "更新成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "项目不存在或无权限访问"},
    },
)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Project:
    project = await project_crud.get_by_id(
        db,
        id=project_id,
        user_id=current_user.id,
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在或无权限访问",
        )

    if project_in.name and project_in.name != project.name:
        existing_project = await project_crud.get_by_name(
            db,
            name=project_in.name,
            user_id=current_user.id,
        )
        if existing_project and existing_project.id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"项目名称 '{project_in.name}' 已存在",
            )

    updated_project = await project_crud.update(
        db,
        db_obj=project,
        obj_in=project_in,
        user_id=current_user.id,
    )
    logger.info(f"用户 {current_user.username} 更新了项目: {project_id}")
    return updated_project


@router.delete(
    "/{project_id}",
    summary="删除项目（软删除）",
    responses={
        200: {"description": "删除成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "项目不存在或无权限访问"},
    },
)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    project = await project_crud.get_by_id(
        db,
        id=project_id,
        user_id=current_user.id,
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在或无权限访问",
        )

    deleted_count = await project_crud.soft_delete(
        db,
        id=project_id,
        user_id=current_user.id,
    )
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除项目失败",
        )

    logger.info(f"用户 {current_user.username} 删除了项目: {project_id}")
    return {
        "success": True,
        "message": f"项目 '{project.name}' 已删除",
        "project_id": project_id,
    }
