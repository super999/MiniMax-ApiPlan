import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from schemas.response import EvaluationResult

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvaluationService:
    def __init__(self):
        self.enable_evaluation = os.getenv("ENABLE_EVALUATION", "false").lower() == "true"
        self.evaluation_model = os.getenv("EVALUATION_MODEL", "abab6.5s-chat")

    async def evaluate(
        self,
        prompt: str,
        response: str,
        model: Optional[str] = None,
        evaluation_config: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        if not self.enable_evaluation:
            logger.info("评测功能未启用，跳过评测")
            return EvaluationResult(
                score=None,
                passed=None,
                details={"message": "评测功能未启用", "evaluated_at": datetime.now().isoformat()},
                error=None
            )

        try:
            result = await self._do_evaluate(
                prompt=prompt,
                response=response,
                model=model,
                config=evaluation_config or {}
            )
            return result
        except Exception as e:
            logger.error(f"评测过程出错: {str(e)}")
            return EvaluationResult(
                score=None,
                passed=False,
                details={"error": str(e), "evaluated_at": datetime.now().isoformat()},
                error=str(e)
            )

    async def _do_evaluate(
        self,
        prompt: str,
        response: str,
        model: Optional[str],
        config: Dict[str, Any]
    ) -> EvaluationResult:
        raise NotImplementedError(
            "具体的评测逻辑需要实现。请根据你的评测需求实现此方法。\n"
            "示例实现方向：\n"
            "1. 基于规则的评测：检查特定关键词、格式要求等\n"
            "2. 基于模型的评测：调用另一个模型来评估回答质量\n"
            "3. 基于参考的评测：与预期答案进行比较\n"
            "4. 代码执行评测：如果是代码生成任务，可以执行代码验证正确性"
        )

    def log_evaluation(
        self,
        prompt: str,
        response: str,
        eval_result: EvaluationResult,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt[:200] if len(prompt) > 200 else prompt,
            "response_length": len(response),
            "score": eval_result.score,
            "passed": eval_result.passed,
            "metadata": metadata or {}
        }
        logger.info(f"评测日志: {log_entry}")

    async def batch_evaluate(
        self,
        test_cases: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        results = []
        for case in test_cases:
            prompt = case.get("prompt", "")
            expected_response = case.get("expected_response", "")
            metadata = case.get("metadata", {})

            from service.minimax_service import MiniMaxService
            minimax_service = MiniMaxService()
            from schemas.request import ChatRequest

            chat_request = ChatRequest(prompt=prompt)
            chat_response = await minimax_service.chat(chat_request)

            eval_result = await self.evaluate(
                prompt=prompt,
                response=chat_response.content or "",
                model=chat_response.model
            )

            results.append({
                "test_case": case,
                "chat_response": chat_response,
                "evaluation": eval_result,
                "passed": eval_result.passed
            })

        return results
