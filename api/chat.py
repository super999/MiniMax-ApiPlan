import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from schemas.request import ChatRequest
from schemas.response import ChatResponse
from service.minimax_service import MiniMaxService

router = APIRouter(prefix="/api", tags=["chat"])

logger = logging.getLogger(__name__)


def get_minimax_service() -> MiniMaxService:
    try:
        return MiniMaxService()
    except ValueError as e:
        logger.error(f"初始化 MiniMaxService 失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse, summary="发送聊天请求")
async def chat(
    request: ChatRequest,
    service: MiniMaxService = Depends(get_minimax_service)
) -> ChatResponse:
    logger.info(f"收到聊天请求，prompt长度: {len(request.prompt)}")

    try:
        response = await service.chat(request)

        if not response.success:
            logger.warning(f"聊天请求失败: {response.error_msg}")
            return response

        logger.info(f"聊天请求成功，响应长度: {len(response.content or '')}")
        return response

    except Exception as e:
        logger.error(f"处理聊天请求时发生错误: {str(e)}", exc_info=True)
        return ChatResponse(
            success=False,
            error_msg=f"服务器内部错误: {str(e)}"
        )


@router.get("/health", summary="健康检查")
async def health_check() -> dict:
    return {"status": "healthy", "message": "服务运行正常"}
