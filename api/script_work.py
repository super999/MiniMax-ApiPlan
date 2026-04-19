from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from core.logger import get_logger
from core.deps import get_current_user
from db.session import get_async_session
from db.crud.script_work import script_work_crud
from db.crud.script_chapter import script_chapter_crud
from db.crud.project import project_crud
from db.models.user import User
from db.models.script_work import (
    ScriptWork,
    ScriptWorkCreate,
    ScriptWorkUpdate,
    ScriptWorkResponse,
    ScriptWorkStatus,
)
from db.models.script_chapter import (
    ScriptChapter,
    ScriptChapterCreate,
    ScriptChapterUpdate,
    ScriptChapterResponse,
    ScriptChapterStatus,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/script-works", tags=["script-works"])


class ScriptWorkDetailResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    outline: Optional[str] = None
    characters: Optional[str] = None
    status: ScriptWorkStatus
    project_id: int
    user_id: int
    is_active: bool
    created_at: Any
    updated_at: Any
    chapters: list[ScriptChapterResponse] = []

    class Config:
        from_attributes = True


class ScriptWorkListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: ScriptWorkStatus
    project_id: int
    chapter_count: int = 0
    created_at: Any
    updated_at: Any

    class Config:
        from_attributes = True


class ChapterCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    chapter_number: Optional[int] = Field(default=None, ge=1)
    outline: Optional[str] = None
    content: Optional[str] = None


class ChapterUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    chapter_number: Optional[int] = Field(default=None, ge=1)
    outline: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ScriptChapterStatus] = None


class OutlineUpdateRequest(BaseModel):
    outline: str


class CharactersUpdateRequest(BaseModel):
    characters: str


async def _validate_project_access(
    db: AsyncSession,
    project_id: int,
    current_user: User,
) -> None:
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


async def _validate_script_work_access(
    db: AsyncSession,
    script_work_id: int,
    current_user: User,
) -> ScriptWork:
    script_work = await script_work_crud.get_by_id(
        db,
        id=script_work_id,
        user_id=current_user.id,
    )
    if not script_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="脚本作品不存在或无权限访问",
        )
    return script_work


async def _validate_chapter_access(
    db: AsyncSession,
    chapter_id: int,
    current_user: User,
) -> ScriptChapter:
    chapter = await script_chapter_crud.get_by_id(
        db,
        id=chapter_id,
        user_id=current_user.id,
    )
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在或无权限访问",
        )
    return chapter


@router.post(
    "",
    response_model=ScriptWorkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建脚本作品",
    responses={
        201: {"description": "脚本作品创建成功"},
        400: {"description": "作品名称已存在"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "项目不存在或无权限访问"},
    },
)
async def create_script_work(
    script_work_in: ScriptWorkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> ScriptWork:
    await _validate_project_access(db, script_work_in.project_id, current_user)

    existing_work = await script_work_crud.get_by_title(
        db,
        title=script_work_in.title,
        project_id=script_work_in.project_id,
        user_id=current_user.id,
    )
    if existing_work:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"作品名称 '{script_work_in.title}' 已存在",
        )

    script_work = await script_work_crud.create(
        db,
        obj_in=script_work_in,
        user_id=current_user.id,
    )
    logger.info(f"用户 {current_user.username} 创建了脚本作品: {script_work.title}")
    return script_work


@router.get(
    "",
    response_model=list[ScriptWorkListResponse],
    summary="获取项目下的所有脚本作品",
    responses={
        200: {"description": "获取成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "项目不存在或无权限访问"},
    },
)
async def get_script_works(
    project_id: int = Query(..., description="项目ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> list[dict[str, Any]]:
    await _validate_project_access(db, project_id, current_user)

    script_works = await script_work_crud.get_by_project(
        db,
        project_id=project_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    result = []
    for work in script_works:
        chapters = await script_chapter_crud.get_by_script_work(
            db,
            script_work_id=work.id,
            user_id=current_user.id,
        )
        result.append({
            "id": work.id,
            "title": work.title,
            "description": work.description,
            "status": work.status,
            "project_id": work.project_id,
            "chapter_count": len(chapters),
            "created_at": work.created_at,
            "updated_at": work.updated_at,
        })

    return result


@router.get(
    "/{script_work_id}",
    response_model=ScriptWorkDetailResponse,
    summary="获取脚本作品详情（含章节列表）",
    responses={
        200: {"description": "获取成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "脚本作品不存在或无权限访问"},
    },
)
async def get_script_work_detail(
    script_work_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    script_work = await _validate_script_work_access(db, script_work_id, current_user)

    chapters = await script_chapter_crud.get_by_script_work(
        db,
        script_work_id=script_work_id,
        user_id=current_user.id,
    )

    return {
        "id": script_work.id,
        "title": script_work.title,
        "description": script_work.description,
        "outline": script_work.outline,
        "characters": script_work.characters,
        "status": script_work.status,
        "project_id": script_work.project_id,
        "user_id": script_work.user_id,
        "is_active": script_work.is_active,
        "created_at": script_work.created_at,
        "updated_at": script_work.updated_at,
        "chapters": [
            ScriptChapterResponse.model_validate(chapter).model_dump()
            for chapter in chapters
        ],
    }


@router.put(
    "/{script_work_id}",
    response_model=ScriptWorkResponse,
    summary="更新脚本作品基本信息",
    responses={
        200: {"description": "更新成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "脚本作品不存在或无权限访问"},
    },
)
async def update_script_work(
    script_work_id: int,
    script_work_in: ScriptWorkUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> ScriptWork:
    script_work = await _validate_script_work_access(db, script_work_id, current_user)

    if script_work_in.title and script_work_in.title != script_work.title:
        existing_work = await script_work_crud.get_by_title(
            db,
            title=script_work_in.title,
            project_id=script_work.project_id,
            user_id=current_user.id,
        )
        if existing_work and existing_work.id != script_work_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"作品名称 '{script_work_in.title}' 已存在",
            )

    updated_work = await script_work_crud.update(
        db,
        db_obj=script_work,
        obj_in=script_work_in,
        user_id=current_user.id,
    )
    logger.info(f"用户 {current_user.username} 更新了脚本作品: {script_work_id}")
    return updated_work


@router.put(
    "/{script_work_id}/outline",
    response_model=ScriptWorkResponse,
    summary="保存脚本作品大纲",
    responses={
        200: {"description": "保存成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "脚本作品不存在或无权限访问"},
    },
)
async def update_script_work_outline(
    script_work_id: int,
    outline_in: OutlineUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> ScriptWork:
    script_work = await _validate_script_work_access(db, script_work_id, current_user)

    updated_work = await script_work_crud.update_outline(
        db,
        script_work_id=script_work_id,
        outline=outline_in.outline,
        user_id=current_user.id,
    )
    logger.info(f"用户 {current_user.username} 更新了脚本作品大纲: {script_work_id}")
    return updated_work


@router.put(
    "/{script_work_id}/characters",
    response_model=ScriptWorkResponse,
    summary="保存脚本作品角色设定",
    responses={
        200: {"description": "保存成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "脚本作品不存在或无权限访问"},
    },
)
async def update_script_work_characters(
    script_work_id: int,
    characters_in: CharactersUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> ScriptWork:
    script_work = await _validate_script_work_access(db, script_work_id, current_user)

    updated_work = await script_work_crud.update_characters(
        db,
        script_work_id=script_work_id,
        characters=characters_in.characters,
        user_id=current_user.id,
    )
    logger.info(f"用户 {current_user.username} 更新了脚本作品角色设定: {script_work_id}")
    return updated_work


@router.delete(
    "/{script_work_id}",
    summary="删除脚本作品（软删除）",
    responses={
        200: {"description": "删除成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "脚本作品不存在或无权限访问"},
    },
)
async def delete_script_work(
    script_work_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    script_work = await _validate_script_work_access(db, script_work_id, current_user)

    deleted_count = await script_work_crud.soft_delete(
        db,
        id=script_work_id,
        user_id=current_user.id,
    )
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除脚本作品失败",
        )

    logger.info(f"用户 {current_user.username} 删除了脚本作品: {script_work_id}")
    return {
        "success": True,
        "message": f"脚本作品 '{script_work.title}' 已删除",
        "script_work_id": script_work_id,
    }


@router.post(
    "/{script_work_id}/chapters",
    response_model=ScriptChapterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建脚本章节",
    responses={
        201: {"description": "章节创建成功"},
        400: {"description": "章节号已存在"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "脚本作品不存在或无权限访问"},
    },
)
async def create_chapter(
    script_work_id: int,
    chapter_in: ChapterCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> ScriptChapter:
    script_work = await _validate_script_work_access(db, script_work_id, current_user)

    chapter_number = chapter_in.chapter_number
    if chapter_number is None:
        max_number = await script_chapter_crud.get_max_chapter_number(
            db,
            script_work_id=script_work_id,
            user_id=current_user.id,
        )
        chapter_number = max_number + 1
    else:
        existing_chapter = await script_chapter_crud.get_by_chapter_number(
            db,
            script_work_id=script_work_id,
            chapter_number=chapter_number,
            user_id=current_user.id,
        )
        if existing_chapter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"章节号 {chapter_number} 已存在",
            )

    chapter_create = ScriptChapterCreate(
        title=chapter_in.title,
        chapter_number=chapter_number,
        script_work_id=script_work_id,
        project_id=script_work.project_id,
        outline=chapter_in.outline,
        content=chapter_in.content,
    )

    chapter = await script_chapter_crud.create(
        db,
        obj_in=chapter_create,
        user_id=current_user.id,
    )
    logger.info(f"用户 {current_user.username} 创建了章节: {chapter.title} (作品: {script_work_id})")
    return chapter


@router.get(
    "/{script_work_id}/chapters/{chapter_id}",
    response_model=ScriptChapterResponse,
    summary="获取章节详情",
    responses={
        200: {"description": "获取成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "章节不存在或无权限访问"},
    },
)
async def get_chapter(
    script_work_id: int,
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> ScriptChapter:
    await _validate_script_work_access(db, script_work_id, current_user)
    chapter = await _validate_chapter_access(db, chapter_id, current_user)

    if chapter.script_work_id != script_work_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不属于该作品",
        )

    return chapter


@router.put(
    "/{script_work_id}/chapters/{chapter_id}",
    response_model=ScriptChapterResponse,
    summary="更新章节内容",
    responses={
        200: {"description": "更新成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "章节不存在或无权限访问"},
    },
)
async def update_chapter(
    script_work_id: int,
    chapter_id: int,
    chapter_in: ChapterUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> ScriptChapter:
    await _validate_script_work_access(db, script_work_id, current_user)
    chapter = await _validate_chapter_access(db, chapter_id, current_user)

    if chapter.script_work_id != script_work_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不属于该作品",
        )

    if chapter_in.chapter_number and chapter_in.chapter_number != chapter.chapter_number:
        existing_chapter = await script_chapter_crud.get_by_chapter_number(
            db,
            script_work_id=script_work_id,
            chapter_number=chapter_in.chapter_number,
            user_id=current_user.id,
        )
        if existing_chapter and existing_chapter.id != chapter_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"章节号 {chapter_in.chapter_number} 已存在",
            )

    update_dict = chapter_in.model_dump(exclude_unset=True)
    update_data = ScriptChapterUpdate(**update_dict)

    updated_chapter = await script_chapter_crud.update(
        db,
        db_obj=chapter,
        obj_in=update_data,
        user_id=current_user.id,
    )
    logger.info(f"用户 {current_user.username} 更新了章节: {chapter_id}")
    return updated_chapter


@router.delete(
    "/{script_work_id}/chapters/{chapter_id}",
    summary="删除章节（软删除）",
    responses={
        200: {"description": "删除成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "章节不存在或无权限访问"},
    },
)
async def delete_chapter(
    script_work_id: int,
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    await _validate_script_work_access(db, script_work_id, current_user)
    chapter = await _validate_chapter_access(db, chapter_id, current_user)

    if chapter.script_work_id != script_work_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不属于该作品",
        )

    deleted_count = await script_chapter_crud.soft_delete(
        db,
        id=chapter_id,
        user_id=current_user.id,
    )
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除章节失败",
        )

    logger.info(f"用户 {current_user.username} 删除了章节: {chapter_id}")
    return {
        "success": True,
        "message": f"章节 '{chapter.title}' 已删除",
        "chapter_id": chapter_id,
    }
