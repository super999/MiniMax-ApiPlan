from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import get_logger
from core.deps import get_current_user
from db.session import get_async_session
from db.models.user import User
from service.script_generation_service import ScriptGenerationService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/script-generation", tags=["script-generation"])


class GenerateOutlineRequest(BaseModel):
    script_work_id: int = Field(..., description="脚本作品ID")
    custom_prompt: Optional[str] = Field(default=None, description="自定义提示词（可选）")


class GenerateCharactersRequest(BaseModel):
    script_work_id: int = Field(..., description="脚本作品ID")
    custom_prompt: Optional[str] = Field(default=None, description="自定义提示词（可选）")


class GenerateChapterRequest(BaseModel):
    script_work_id: int = Field(..., description="脚本作品ID")
    chapter_id: int = Field(..., description="章节ID")
    custom_prompt: Optional[str] = Field(default=None, description="自定义提示词（可选）")


class GenerationResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    model: Optional[str] = None
    latency_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    error_msg: Optional[str] = None


async def _get_generation_service(
    db: AsyncSession,
) -> ScriptGenerationService:
    return ScriptGenerationService(db_session=db)


@router.post(
    "/generate-outline",
    response_model=GenerationResponse,
    summary="AI生成脚本大纲",
    responses={
        200: {"description": "生成成功"},
        400: {"description": "请求参数错误"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "脚本作品不存在或无权限访问"},
        500: {"description": "生成失败"},
    },
)
async def generate_outline(
    request: GenerateOutlineRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> GenerationResponse:
    logger.info(f"用户 {current_user.username} 请求生成大纲，作品ID: {request.script_work_id}")

    try:
        async with ScriptGenerationService(db_session=db) as service:
            result = await service.generate_outline(
                script_work_id=request.script_work_id,
                user_id=current_user.id,
                custom_prompt=request.custom_prompt,
            )

        if result["success"]:
            return GenerationResponse(
                success=True,
                content=result["content"],
                model=result.get("model"),
                latency_ms=result.get("latency_ms"),
                tokens_used=result.get("tokens_used"),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error_msg", "生成失败"),
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成大纲时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失败: {str(e)}",
        )


@router.post(
    "/generate-characters",
    response_model=GenerationResponse,
    summary="AI生成人物设定",
    responses={
        200: {"description": "生成成功"},
        400: {"description": "请求参数错误"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "脚本作品不存在或无权限访问"},
        500: {"description": "生成失败"},
    },
)
async def generate_characters(
    request: GenerateCharactersRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> GenerationResponse:
    logger.info(f"用户 {current_user.username} 请求生成人物设定，作品ID: {request.script_work_id}")

    try:
        async with ScriptGenerationService(db_session=db) as service:
            result = await service.generate_characters(
                script_work_id=request.script_work_id,
                user_id=current_user.id,
                custom_prompt=request.custom_prompt,
            )

        if result["success"]:
            return GenerationResponse(
                success=True,
                content=result["content"],
                model=result.get("model"),
                latency_ms=result.get("latency_ms"),
                tokens_used=result.get("tokens_used"),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error_msg", "生成失败"),
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成人物设定时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失败: {str(e)}",
        )


@router.post(
    "/generate-chapter",
    response_model=GenerationResponse,
    summary="AI生成分集/分场内容",
    responses={
        200: {"description": "生成成功"},
        400: {"description": "请求参数错误"},
        401: {"description": "未授权，请先登录"},
        404: {"description": "脚本作品或章节不存在或无权限访问"},
        500: {"description": "生成失败"},
    },
)
async def generate_chapter(
    request: GenerateChapterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> GenerationResponse:
    logger.info(f"用户 {current_user.username} 请求生成章节内容，作品ID: {request.script_work_id}, 章节ID: {request.chapter_id}")

    try:
        async with ScriptGenerationService(db_session=db) as service:
            result = await service.generate_chapter_content(
                script_work_id=request.script_work_id,
                chapter_id=request.chapter_id,
                user_id=current_user.id,
                custom_prompt=request.custom_prompt,
            )

        if result["success"]:
            return GenerationResponse(
                success=True,
                content=result["content"],
                model=result.get("model"),
                latency_ms=result.get("latency_ms"),
                tokens_used=result.get("tokens_used"),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error_msg", "生成失败"),
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成章节内容时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失败: {str(e)}",
        )
