from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import get_logger
from core.settings import settings
from core.deps import get_current_user
from db.session import get_async_session, is_database_configured
from db.models.user import User
from schemas.request import ChatRequest
from schemas.response import ChatResponse
from service.chat_service import ChatService
from clients.minimax_client import MiniMaxClient

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


async def get_minimax_client() -> Optional[MiniMaxClient]:
    try:
        return MiniMaxClient()
    except ValueError as e:
        logger.error(f"初始化 MiniMaxClient 失败: {e}")
        return None


async def get_db_session_dependency() -> Optional[AsyncSession]:
    if not is_database_configured():
        yield None
    else:
        async for session in get_async_session():
            yield session


async def get_chat_service(
    minimax_client: Optional[MiniMaxClient] = Depends(get_minimax_client),
    db_session: Optional[AsyncSession] = Depends(get_db_session_dependency),
) -> ChatService:
    if minimax_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MiniMax API 未配置，请检查环境变量",
        )
    return ChatService(minimax_client=minimax_client, db_session=db_session)


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="发送聊天请求",
    responses={
        200: {"description": "请求成功"},
        400: {"description": "请求参数错误"},
        401: {"description": "未授权，请先登录"},
        503: {"description": "服务不可用（API 未配置）"},
    },
)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    logger.info(f"收到聊天请求，prompt 长度: {len(request.prompt)}")

    try:
        response = await service.chat(request)

        if not response.success:
            logger.warning(f"聊天请求失败: {response.error_msg}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理聊天请求时发生错误: {str(e)}", exc_info=True)
        return ChatResponse(
            success=False,
            error_msg="服务器内部错误，请稍后重试"
            if not settings.app.debug
            else f"服务器内部错误: {str(e)}",
        )


@router.post(
    "/chat/with-evaluation",
    summary="发送聊天请求并进行评测",
)
async def chat_with_evaluation(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    logger.info(f"收到带评测的聊天请求，prompt 长度: {len(request.prompt)}")

    try:
        result = await service.chat_with_evaluation(request)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理带评测的聊天请求时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误，请稍后重试",
        )
