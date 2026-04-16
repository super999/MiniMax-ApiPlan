import os
import time
import httpx
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from schemas.request import ChatRequest
from schemas.response import ChatResponse, MiniMaxResponse, MiniMaxUsage


load_dotenv()


class MiniMaxService:
    def __init__(self):
        self.api_key = os.getenv("MINIMAX_API_KEY")
        self.group_id = os.getenv("MINIMAX_GROUP_ID")
        self.base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1/text/chatcompletion_v2")
        self.default_model = os.getenv("MINIMAX_DEFAULT_MODEL", "abab6.5s-chat")
        self.timeout = float(os.getenv("MINIMAX_TIMEOUT", "60.0"))

        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY 未设置，请在 .env 文件中配置")

    def _build_request_body(self, request: ChatRequest) -> Dict[str, Any]:
        model = request.model or self.default_model
        return {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": request.prompt
                }
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

    def _build_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        return headers

    def _build_query_params(self) -> Dict[str, str]:
        params = {}
        if self.group_id:
            params["GroupId"] = self.group_id
        return params

    async def chat(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        request_id = None

        try:
            body = self._build_request_body(request)
            headers = self._build_headers()
            params = self._build_query_params()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    json=body,
                    headers=headers,
                    params=params,
                )

                latency_ms = (time.time() - start_time) * 1000

                if response.status_code != 200:
                    error_msg = f"API请求失败，状态码: {response.status_code}, 响应: {response.text}"
                    return ChatResponse(
                        success=False,
                        error_msg=error_msg,
                        latency_ms=latency_ms
                    )

                response_data = response.json()
                request_id = response_data.get("id")

                minimax_response = MiniMaxResponse(**response_data)
                content = minimax_response.get_content()

                usage = None
                if response_data.get("usage"):
                    usage_data = response_data["usage"]
                    usage = MiniMaxUsage(
                        total_tokens=usage_data.get("total_tokens", 0),
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0)
                    )

                return ChatResponse(
                    success=True,
                    content=content,
                    model=minimax_response.model or request.model,
                    usage=usage,
                    request_id=request_id,
                    latency_ms=round(latency_ms, 2)
                )

        except httpx.TimeoutException:
            latency_ms = (time.time() - start_time) * 1000
            return ChatResponse(
                success=False,
                error_msg="请求超时，请稍后重试",
                latency_ms=latency_ms,
                request_id=request_id
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return ChatResponse(
                success=False,
                error_msg=f"发生错误: {str(e)}",
                latency_ms=latency_ms,
                request_id=request_id
            )

    async def chat_with_evaluation(self, request: ChatRequest) -> Dict[str, Any]:
        chat_response = await self.chat(request)

        result = {
            "chat_response": chat_response,
            "evaluation": None
        }

        if chat_response.success and chat_response.content:
            from service.evaluation_service import EvaluationService
            eval_service = EvaluationService()
            eval_result = await eval_service.evaluate(
                prompt=request.prompt,
                response=chat_response.content,
                model=chat_response.model
            )
            result["evaluation"] = eval_result

        return result
