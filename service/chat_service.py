from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from clients.minimax_client import (
    MiniMaxClient,
    MiniMaxResponseData,
    MiniMaxError,
)
from core.logger import get_logger
from core.settings import settings
from db.crud.chat_log import chat_log_crud
from db.models.chat_log import ChatLogCreate
from schemas.request import ChatRequest
from schemas.response import ChatResponse, MiniMaxUsage

logger = get_logger(__name__)


class ChatService:
    def __init__(
        self,
        minimax_client: Optional[MiniMaxClient] = None,
        db_session: Optional[AsyncSession] = None,
    ):
        self._minimax_client = minimax_client
        self._db_session = db_session
        self._owns_client = minimax_client is None

    def _get_client(self) -> MiniMaxClient:
        if self._minimax_client is None:
            self._minimax_client = MiniMaxClient()
            self._owns_client = True
        return self._minimax_client

    def _to_chat_response(
        self,
        response_data: Optional[MiniMaxResponseData],
        error: Optional[MiniMaxError],
        latency_ms: float,
        model_used: Optional[str] = None,
    ) -> ChatResponse:
        if response_data and error is None:
            usage = None
            if response_data.usage:
                usage = MiniMaxUsage(
                    total_tokens=response_data.usage.total_tokens,
                    prompt_tokens=response_data.usage.prompt_tokens,
                    completion_tokens=response_data.usage.completion_tokens,
                )

            return ChatResponse(
                success=True,
                content=response_data.content,
                model=response_data.model or model_used,
                usage=usage,
                request_id=response_data.id,
                latency_ms=round(latency_ms, 2),
            )

        error_msg = "未知错误"
        if error:
            error_msg = error.message
        return ChatResponse(
            success=False,
            error_msg=error_msg,
            latency_ms=round(latency_ms, 2),
        )

    async def _log_to_database(
        self,
        request: ChatRequest,
        response: ChatResponse,
    ) -> None:
        if self._db_session is None:
            return

        try:
            log_entry = ChatLogCreate(
                request_id=response.request_id,
                model_name=response.model,
                prompt=request.prompt,
                response=response.content,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                total_tokens=response.usage.total_tokens if response.usage else None,
                prompt_tokens=response.usage.prompt_tokens if response.usage else None,
                completion_tokens=response.usage.completion_tokens if response.usage else None,
                latency_ms=response.latency_ms,
                success=response.success,
                error_msg=response.error_msg,
                meta_data=None,
            )
            await chat_log_crud.create(self._db_session, log_entry)
        except Exception as e:
            logger.error(f"记录聊天日志到数据库失败: {str(e)}", exc_info=True)

    async def chat(self, request: ChatRequest) -> ChatResponse:
        client = self._get_client()

        logger.info(f"处理聊天请求，prompt 长度: {len(request.prompt)}")

        response_data, error, latency_ms = await client.chat(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 2048,
        )

        response = self._to_chat_response(
            response_data=response_data,
            error=error,
            latency_ms=latency_ms,
            model_used=request.model,
        )

        if response.success:
            logger.info(
                f"聊天请求成功，响应长度: {len(response.content or '')}，耗时: {response.latency_ms:.2f}ms"
            )
        else:
            logger.warning(f"聊天请求失败: {response.error_msg}")

        if self._db_session is not None:
            await self._log_to_database(request, response)

        return response

    async def chat_with_evaluation(
        self,
        request: ChatRequest,
        evaluation_service: Optional[Any] = None,
    ) -> dict[str, Any]:
        chat_response = await self.chat(request)

        result = {
            "chat_response": chat_response,
            "evaluation": None,
        }

        if not settings.evaluation.enabled:
            logger.info("评测功能未启用")
            return result

        if not chat_response.success or not chat_response.content:
            logger.warning("聊天请求失败或无内容，跳过评测")
            return result

        if evaluation_service is None:
            from service.evaluation_service import EvaluationService

            evaluation_service = EvaluationService(
                minimax_client=self._minimax_client
            )

        eval_result = await evaluation_service.evaluate(
            prompt=request.prompt,
            response=chat_response.content,
            model=chat_response.model,
        )
        result["evaluation"] = eval_result

        return result

    async def close(self) -> None:
        if self._owns_client and self._minimax_client is not None:
            await self._minimax_client.close()
            self._minimax_client = None

    async def __aenter__(self) -> "ChatService":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
