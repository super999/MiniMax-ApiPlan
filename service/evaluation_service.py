from typing import Any, Dict, Optional
from datetime import datetime

from clients.minimax_client import MiniMaxClient
from core.logger import get_logger
from core.settings import settings
from schemas.response import EvaluationResult

logger = get_logger(__name__)


class EvaluationService:
    def __init__(
        self,
        enabled: Optional[bool] = None,
        evaluation_model: Optional[str] = None,
        minimax_client: Optional[MiniMaxClient] = None,
    ):
        self._enabled = enabled if enabled is not None else settings.evaluation.enabled
        self._evaluation_model = (
            evaluation_model or settings.evaluation.model
        )
        self._minimax_client = minimax_client
        self._owns_client = minimax_client is None

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def evaluation_model(self) -> str:
        return self._evaluation_model

    def _get_client(self) -> Optional[MiniMaxClient]:
        if self._minimax_client is None and self._enabled:
            try:
                self._minimax_client = MiniMaxClient()
                self._owns_client = True
            except ValueError as e:
                logger.warning(f"无法初始化 MiniMax 客户端，评测功能将不可用: {e}")
                self._enabled = False
        return self._minimax_client

    async def evaluate(
        self,
        prompt: str,
        response: str,
        model: Optional[str] = None,
        evaluation_config: Optional[Dict[str, Any]] = None,
    ) -> EvaluationResult:
        if not self._enabled:
            logger.info("评测功能未启用，跳过评测")
            return EvaluationResult(
                score=None,
                passed=None,
                details={
                    "message": "评测功能未启用",
                    "evaluated_at": datetime.now().isoformat(),
                },
                error=None,
            )

        try:
            result = await self._do_evaluate(
                prompt=prompt,
                response=response,
                model=model,
                config=evaluation_config or {},
            )
            self._log_evaluation(
                prompt=prompt,
                response=response,
                eval_result=result,
                metadata={
                    "model": model,
                    "evaluation_model": self._evaluation_model,
                },
            )
            return result
        except Exception as e:
            logger.error(f"评测过程出错: {str(e)}", exc_info=True)
            return EvaluationResult(
                score=None,
                passed=False,
                details={
                    "error": str(e),
                    "evaluated_at": datetime.now().isoformat(),
                },
                error=str(e),
            )

    async def _do_evaluate(
        self,
        prompt: str,
        response: str,
        model: Optional[str],
        config: Dict[str, Any],
    ) -> EvaluationResult:
        return EvaluationResult(
            score=None,
            passed=True,
            details={
                "message": "评测功能已启用但未实现具体逻辑",
                "evaluated_at": datetime.now().isoformat(),
                "model_used": model,
                "evaluation_model": self._evaluation_model,
                "config": config,
            },
            error=None,
        )

    def _log_evaluation(
        self,
        prompt: str,
        response: str,
        eval_result: EvaluationResult,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt[:200] if len(prompt) > 200 else prompt,
            "response_length": len(response),
            "score": eval_result.score,
            "passed": eval_result.passed,
            "metadata": metadata or {},
        }
        logger.info(f"评测日志: {log_entry}")

    async def batch_evaluate(
        self,
        test_cases: list[Dict[str, Any]],
    ) -> list[Dict[str, Any]]:
        results = []

        for case in test_cases:
            prompt = case.get("prompt", "")
            expected_response = case.get("expected_response", "")
            metadata = case.get("metadata", {})

            chat_service = ChatService(minimax_client=self._minimax_client)
            from schemas.request import ChatRequest

            chat_request = ChatRequest(prompt=prompt)
            chat_response = await chat_service.chat(chat_request)

            eval_result = await self.evaluate(
                prompt=prompt,
                response=chat_response.content or "",
                model=chat_response.model,
            )

            results.append(
                {
                    "test_case": case,
                    "chat_response": chat_response,
                    "evaluation": eval_result,
                    "passed": eval_result.passed,
                }
            )

        return results

    async def close(self) -> None:
        if self._owns_client and self._minimax_client is not None:
            await self._minimax_client.close()
            self._minimax_client = None

    async def __aenter__(self) -> "EvaluationService":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


from service.chat_service import ChatService
