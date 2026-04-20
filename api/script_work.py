from datetime import datetime
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from core.logger import get_logger
from core.deps import get_current_user
from core.prompts import render_prompt, GenerationType as PromptGenerationType
from db.session import get_async_session
from db.crud.script_work import script_work_crud
from db.crud.script_chapter import script_chapter_crud
from db.crud.project import project_crud
from db.crud.generation_record import generation_record_crud
from clients.minimax_client import MiniMaxClient
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
from db.models.generation_record import (
    GenerationType,
    GenerationStatus,
    GenerationRecordCreate,
    GenerationRecordUpdate,
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


class OutlineGenerateRequest(BaseModel):
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=4096, ge=1, le=8192)


class OutlineGenerateResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    generation_record_id: Optional[int] = None


class CharactersGenerateRequest(BaseModel):
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=4096, ge=1, le=8192)


class CharactersGenerateResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    generation_record_id: Optional[int] = None


class ChapterOutlineGenerateRequest(BaseModel):
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=4096, ge=1, le=8192)


class ChapterOutlineGenerateResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    generation_record_id: Optional[int] = None


class ChapterContentGenerateRequest(BaseModel):
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=4096, ge=1, le=8192)
    genre: Optional[str] = None
    tone: Optional[str] = None
    audience: Optional[str] = None
    word_count: Optional[int] = None


class ChapterContentGenerateResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    generation_record_id: Optional[int] = None


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


@router.post(
    "/{script_work_id}/generate-outline",
    response_model=OutlineGenerateResponse,
    summary="AI 生成大纲",
    responses={
        200: {"description": "生成成功"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "脚本作品不存在或无权限访问"},
        500: {"description": "AI 生成失败"},
    },
)
async def generate_outline(
    script_work_id: int,
    request: Optional[OutlineGenerateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> OutlineGenerateResponse:
    script_work = await _validate_script_work_access(db, script_work_id, current_user)

    generation_record = None
    started_at = datetime.utcnow()

    try:
        record_create = GenerationRecordCreate(
            generation_type=GenerationType.OUTLINE,
            script_work_id=script_work_id,
            project_id=script_work.project_id,
            prompt=None,
        )
        generation_record = await generation_record_crud.create(
            db,
            obj_in=record_create,
            user_id=current_user.id,
        )
        logger.info(
            f"用户 {current_user.username} 开始生成大纲，作品: {script_work_id}, 记录ID: {generation_record.id}"
        )

        prompt_context = {
            "title": script_work.title or "",
            "description": script_work.description or "",
        }
        prompt = render_prompt(PromptGenerationType.OUTLINE, prompt_context)

        temperature = request.temperature if request else 0.7
        max_tokens = request.max_tokens if request else 4096

        async with MiniMaxClient() as client:
            response, error, latency_ms = await client.chat(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        completed_at = datetime.utcnow()

        if error or response is None:
            error_msg = error.message if error else "AI 生成失败，无响应数据"
            logger.error(f"大纲生成失败: {error_msg}, 记录ID: {generation_record.id}")

            await generation_record_crud.update_status(
                db,
                record_id=generation_record.id,
                status=GenerationStatus.FAILED,
                user_id=current_user.id,
                error_message=error_msg,
            )

            return OutlineGenerateResponse(
                success=False,
                error=error_msg,
                generation_record_id=generation_record.id,
            )

        tokens_used = response.usage.total_tokens if response.usage else None

        await generation_record_crud.update_status(
            db,
            record_id=generation_record.id,
            status=GenerationStatus.COMPLETED,
            user_id=current_user.id,
            result=response.content,
            tokens_used=tokens_used,
        )

        await generation_record_crud.update(
            db,
            db_obj=generation_record,
            obj_in=GenerationRecordUpdate(
                model_used=response.model,
                started_at=started_at,
                completed_at=completed_at,
            ),
            user_id=current_user.id,
        )

        logger.info(
            f"大纲生成成功，作品: {script_work_id}, 记录ID: {generation_record.id}, "
            f"模型: {response.model}, tokens: {tokens_used}, 耗时: {latency_ms:.2f}ms"
        )

        return OutlineGenerateResponse(
            success=True,
            content=response.content,
            generation_record_id=generation_record.id,
        )

    except HTTPException:
        raise

    except Exception as e:
        error_msg = f"大纲生成过程中发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)

        if generation_record:
            await generation_record_crud.update_status(
                db,
                record_id=generation_record.id,
                status=GenerationStatus.FAILED,
                user_id=current_user.id,
                error_message=error_msg,
            )

        return OutlineGenerateResponse(
            success=False,
            error=error_msg,
            generation_record_id=generation_record.id if generation_record else None,
        )


@router.post(
    "/{script_work_id}/generate-characters",
    response_model=CharactersGenerateResponse,
    summary="AI 生成人物设定",
    responses={
        200: {"description": "生成成功"},
        400: {"description": "大纲为空，请先保存大纲"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "脚本作品不存在或无权限访问"},
        500: {"description": "AI 生成失败"},
    },
)
async def generate_characters(
    script_work_id: int,
    request: Optional[CharactersGenerateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> CharactersGenerateResponse:
    script_work = await _validate_script_work_access(db, script_work_id, current_user)

    if not script_work.outline or not script_work.outline.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先保存大纲",
        )

    generation_record = None
    started_at = datetime.utcnow()

    try:
        record_create = GenerationRecordCreate(
            generation_type=GenerationType.CHARACTERS,
            script_work_id=script_work_id,
            project_id=script_work.project_id,
            prompt=None,
        )
        generation_record = await generation_record_crud.create(
            db,
            obj_in=record_create,
            user_id=current_user.id,
        )
        logger.info(
            f"用户 {current_user.username} 开始生成人物设定，作品: {script_work_id}, 记录ID: {generation_record.id}"
        )

        prompt_context = {
            "title": script_work.title or "",
            "description": script_work.description or "",
            "outline": script_work.outline or "",
        }
        prompt = render_prompt(PromptGenerationType.CHARACTERS, prompt_context)

        temperature = request.temperature if request else 0.7
        max_tokens = request.max_tokens if request else 4096

        async with MiniMaxClient() as client:
            response, error, latency_ms = await client.chat(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        completed_at = datetime.utcnow()

        if error or response is None:
            error_msg = error.message if error else "AI 生成失败，无响应数据"
            logger.error(f"人物设定生成失败: {error_msg}, 记录ID: {generation_record.id}")

            await generation_record_crud.update_status(
                db,
                record_id=generation_record.id,
                status=GenerationStatus.FAILED,
                user_id=current_user.id,
                error_message=error_msg,
            )

            return CharactersGenerateResponse(
                success=False,
                error=error_msg,
                generation_record_id=generation_record.id,
            )

        tokens_used = response.usage.total_tokens if response.usage else None

        await generation_record_crud.update_status(
            db,
            record_id=generation_record.id,
            status=GenerationStatus.COMPLETED,
            user_id=current_user.id,
            result=response.content,
            tokens_used=tokens_used,
        )

        await generation_record_crud.update(
            db,
            db_obj=generation_record,
            obj_in=GenerationRecordUpdate(
                model_used=response.model,
                started_at=started_at,
                completed_at=completed_at,
            ),
            user_id=current_user.id,
        )

        logger.info(
            f"人物设定生成成功，作品: {script_work_id}, 记录ID: {generation_record.id}, "
            f"模型: {response.model}, tokens: {tokens_used}, 耗时: {latency_ms:.2f}ms"
        )

        return CharactersGenerateResponse(
            success=True,
            content=response.content,
            generation_record_id=generation_record.id,
        )

    except HTTPException:
        raise

    except Exception as e:
        error_msg = f"人物设定生成过程中发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)

        if generation_record:
            await generation_record_crud.update_status(
                db,
                record_id=generation_record.id,
                status=GenerationStatus.FAILED,
                user_id=current_user.id,
                error_message=error_msg,
            )

        return CharactersGenerateResponse(
            success=False,
            error=error_msg,
            generation_record_id=generation_record.id if generation_record else None,
        )


@router.post(
    "/{script_work_id}/chapters/{chapter_id}/generate-outline",
    response_model=ChapterOutlineGenerateResponse,
    summary="AI 生成本集大纲",
    responses={
        200: {"description": "生成成功"},
        400: {"description": "作品大纲为空，请先保存大纲"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "作品或章节不存在或无权限访问"},
        500: {"description": "AI 生成失败"},
    },
)
async def generate_chapter_outline(
    script_work_id: int,
    chapter_id: int,
    request: Optional[ChapterOutlineGenerateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> ChapterOutlineGenerateResponse:
    script_work = await _validate_script_work_access(db, script_work_id, current_user)
    chapter = await _validate_chapter_access(db, chapter_id, current_user)

    if chapter.script_work_id != script_work_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不属于该作品",
        )

    if not script_work.outline or not script_work.outline.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先保存作品大纲",
        )

    chapters = await script_chapter_crud.get_by_script_work(
        db,
        script_work_id=script_work_id,
        user_id=current_user.id,
    )
    total_chapters = len(chapters)

    generation_record = None
    started_at = datetime.utcnow()

    try:
        record_create = GenerationRecordCreate(
            generation_type=GenerationType.CHAPTER_OUTLINE,
            script_work_id=script_work_id,
            script_chapter_id=chapter_id,
            project_id=script_work.project_id,
            prompt=None,
        )
        generation_record = await generation_record_crud.create(
            db,
            obj_in=record_create,
            user_id=current_user.id,
        )
        logger.info(
            f"用户 {current_user.username} 开始生成章节大纲，作品: {script_work_id}, "
            f"章节: {chapter_id}, 记录ID: {generation_record.id}"
        )

        prompt_context = {
            "outline": script_work.outline or "",
            "characters": script_work.characters or "",
            "chapter_title": chapter.title or "",
            "chapter_number": chapter.chapter_number,
            "total_chapters": total_chapters,
        }
        prompt = render_prompt(PromptGenerationType.CHAPTER_OUTLINE, prompt_context)

        temperature = request.temperature if request else 0.7
        max_tokens = request.max_tokens if request else 4096

        async with MiniMaxClient() as client:
            response, error, latency_ms = await client.chat(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        completed_at = datetime.utcnow()

        if error or response is None:
            error_msg = error.message if error else "AI 生成失败，无响应数据"
            logger.error(f"章节大纲生成失败: {error_msg}, 记录ID: {generation_record.id}")

            await generation_record_crud.update_status(
                db,
                record_id=generation_record.id,
                status=GenerationStatus.FAILED,
                user_id=current_user.id,
                error_message=error_msg,
            )

            return ChapterOutlineGenerateResponse(
                success=False,
                error=error_msg,
                generation_record_id=generation_record.id,
            )

        tokens_used = response.usage.total_tokens if response.usage else None

        await generation_record_crud.update_status(
            db,
            record_id=generation_record.id,
            status=GenerationStatus.COMPLETED,
            user_id=current_user.id,
            result=response.content,
            tokens_used=tokens_used,
        )

        await generation_record_crud.update(
            db,
            db_obj=generation_record,
            obj_in=GenerationRecordUpdate(
                model_used=response.model,
                started_at=started_at,
                completed_at=completed_at,
            ),
            user_id=current_user.id,
        )

        logger.info(
            f"章节大纲生成成功，作品: {script_work_id}, 章节: {chapter_id}, "
            f"记录ID: {generation_record.id}, 模型: {response.model}, "
            f"tokens: {tokens_used}, 耗时: {latency_ms:.2f}ms"
        )

        return ChapterOutlineGenerateResponse(
            success=True,
            content=response.content,
            generation_record_id=generation_record.id,
        )

    except HTTPException:
        raise

    except Exception as e:
        error_msg = f"章节大纲生成过程中发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)

        if generation_record:
            await generation_record_crud.update_status(
                db,
                record_id=generation_record.id,
                status=GenerationStatus.FAILED,
                user_id=current_user.id,
                error_message=error_msg,
            )

        return ChapterOutlineGenerateResponse(
            success=False,
            error=error_msg,
            generation_record_id=generation_record.id if generation_record else None,
        )


@router.post(
    "/{script_work_id}/chapters/{chapter_id}/generate-content",
    response_model=ChapterContentGenerateResponse,
    summary="AI 生成本集内容",
    responses={
        200: {"description": "生成成功"},
        400: {"description": "作品大纲为空，请先保存大纲"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "作品或章节不存在或无权限访问"},
        500: {"description": "AI 生成失败"},
    },
)
async def generate_chapter_content(
    script_work_id: int,
    chapter_id: int,
    request: Optional[ChapterContentGenerateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> ChapterContentGenerateResponse:
    script_work = await _validate_script_work_access(db, script_work_id, current_user)
    chapter = await _validate_chapter_access(db, chapter_id, current_user)

    if chapter.script_work_id != script_work_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不属于该作品",
        )

    if not script_work.outline or not script_work.outline.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先保存作品大纲",
        )

    chapters = await script_chapter_crud.get_by_script_work(
        db,
        script_work_id=script_work_id,
        user_id=current_user.id,
    )
    total_chapters = len(chapters)

    generation_record = None
    started_at = datetime.utcnow()

    try:
        record_create = GenerationRecordCreate(
            generation_type=GenerationType.CHAPTER_CONTENT,
            script_work_id=script_work_id,
            script_chapter_id=chapter_id,
            project_id=script_work.project_id,
            prompt=None,
        )
        generation_record = await generation_record_crud.create(
            db,
            obj_in=record_create,
            user_id=current_user.id,
        )
        logger.info(
            f"用户 {current_user.username} 开始生成章节内容，作品: {script_work_id}, "
            f"章节: {chapter_id}, 记录ID: {generation_record.id}"
        )

        prompt_context = {
            "outline": script_work.outline or "",
            "characters": script_work.characters or "",
            "chapter_title": chapter.title or "",
            "chapter_number": chapter.chapter_number,
            "total_chapters": total_chapters,
            "chapter_outline": chapter.outline or "",
            "genre": request.genre if request and request.genre else "悬疑/甜宠/爽文/玄幻",
            "tone": request.tone if request and request.tone else "轻松幽默/紧张刺激/深情虐恋",
            "audience": request.audience if request and request.audience else "女性向/男性向/全年龄",
            "word_count": request.word_count if request and request.word_count else "300-800字/集",
        }
        prompt = render_prompt(PromptGenerationType.CHAPTER_CONTENT, prompt_context)

        temperature = request.temperature if request else 0.7
        max_tokens = request.max_tokens if request else 4096

        async with MiniMaxClient() as client:
            response, error, latency_ms = await client.chat(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        completed_at = datetime.utcnow()

        if error or response is None:
            error_msg = error.message if error else "AI 生成失败，无响应数据"
            logger.error(f"章节内容生成失败: {error_msg}, 记录ID: {generation_record.id}")

            await generation_record_crud.update_status(
                db,
                record_id=generation_record.id,
                status=GenerationStatus.FAILED,
                user_id=current_user.id,
                error_message=error_msg,
            )

            return ChapterContentGenerateResponse(
                success=False,
                error=error_msg,
                generation_record_id=generation_record.id,
            )

        tokens_used = response.usage.total_tokens if response.usage else None

        await generation_record_crud.update_status(
            db,
            record_id=generation_record.id,
            status=GenerationStatus.COMPLETED,
            user_id=current_user.id,
            result=response.content,
            tokens_used=tokens_used,
        )

        await generation_record_crud.update(
            db,
            db_obj=generation_record,
            obj_in=GenerationRecordUpdate(
                model_used=response.model,
                started_at=started_at,
                completed_at=completed_at,
            ),
            user_id=current_user.id,
        )

        logger.info(
            f"章节内容生成成功，作品: {script_work_id}, 章节: {chapter_id}, "
            f"记录ID: {generation_record.id}, 模型: {response.model}, "
            f"tokens: {tokens_used}, 耗时: {latency_ms:.2f}ms"
        )

        return ChapterContentGenerateResponse(
            success=True,
            content=response.content,
            generation_record_id=generation_record.id,
        )

    except HTTPException:
        raise

    except Exception as e:
        error_msg = f"章节内容生成过程中发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)

        if generation_record:
            await generation_record_crud.update_status(
                db,
                record_id=generation_record.id,
                status=GenerationStatus.FAILED,
                user_id=current_user.id,
                error_message=error_msg,
            )

        return ChapterContentGenerateResponse(
            success=False,
            error=error_msg,
            generation_record_id=generation_record.id if generation_record else None,
        )
