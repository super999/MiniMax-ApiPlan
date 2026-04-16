import time
from dataclasses import dataclass
from typing import Any, Optional
import httpx

from core.settings import settings, MiniMaxSettings
from core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MiniMaxUsageData:
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0


@dataclass
class MiniMaxResponseData:
    id: Optional[str] = None
    model: Optional[str] = None
    content: str = ""
    usage: Optional[MiniMaxUsageData] = None
    raw_response: Optional[dict] = None


@dataclass
class MiniMaxError:
    code: int
    message: str
    raw_error: Optional[dict] = None


class MiniMaxClient:
    def __init__(
        self,
        settings_obj: Optional[MiniMaxSettings] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self._settings = settings_obj or settings.minimax
        self._http_client = http_client
        self._owns_client = http_client is None

        self._validate_config()

    def _validate_config(self) -> None:
        if not self._settings.api_key:
            raise ValueError("MINIMAX_API_KEY 未配置，请设置环境变量")

    @property
    def api_key(self) -> str:
        return self._settings.api_key

    @property
    def group_id(self) -> Optional[str]:
        return self._settings.group_id

    @property
    def base_url(self) -> str:
        return self._settings.base_url

    @property
    def default_model(self) -> str:
        return self._settings.default_model

    @property
    def timeout(self) -> float:
        return self._settings.timeout

    def _get_http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=self.timeout)
            self._owns_client = True
        return self._http_client

    def _build_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _build_query_params(self) -> dict[str, str]:
        params = {}
        if self.group_id:
            params["GroupId"] = self.group_id
        return params

    def _build_request_body(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        return {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    def _parse_response(self, response_data: dict[str, Any]) -> MiniMaxResponseData:
        response = MiniMaxResponseData(raw_response=response_data)

        response.id = response_data.get("id")
        response.model = response_data.get("model")

        choices = response_data.get("choices", [])
        if choices and len(choices) > 0:
            choice = choices[0]
            if isinstance(choice, dict):
                message = choice.get("message", {})
                if isinstance(message, dict):
                    response.content = message.get("content", "")

        usage_data = response_data.get("usage")
        if usage_data and isinstance(usage_data, dict):
            response.usage = MiniMaxUsageData(
                total_tokens=usage_data.get("total_tokens", 0),
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
            )

        return response

    async def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> tuple[Optional[MiniMaxResponseData], Optional[MiniMaxError], float]:
        start_time = time.time()
        client = self._get_http_client()

        try:
            body = self._build_request_body(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt,
            )
            headers = self._build_headers()
            params = self._build_query_params()

            logger.debug(f"发送请求到 MiniMax API: model={body.get('model')}")

            response = await client.post(
                self.base_url,
                json=body,
                headers=headers,
                params=params,
            )

            latency_ms = (time.time() - start_time) * 1000

            if response.status_code != 200:
                error_msg = f"API请求失败，状态码: {response.status_code}"
                logger.error(f"{error_msg}, 响应: {response.text[:500]}")
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {"detail": response.text}
                return (
                    None,
                    MiniMaxError(
                        code=response.status_code,
                        message=error_msg,
                        raw_error=error_data,
                    ),
                    latency_ms,
                )

            response_data = response.json()
            result = self._parse_response(response_data)

            logger.debug(f"MiniMax API 响应成功，耗时: {latency_ms:.2f}ms")
            return result, None, latency_ms

        except httpx.TimeoutException:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"MiniMax API 请求超时，耗时: {latency_ms:.2f}ms")
            return (
                None,
                MiniMaxError(code=408, message="请求超时，请稍后重试"),
                latency_ms,
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"MiniMax API 调用出错: {str(e)}", exc_info=True)
            return (
                None,
                MiniMaxError(code=500, message=f"发生错误: {str(e)}"),
                latency_ms,
            )

    async def close(self) -> None:
        if self._owns_client and self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self) -> "MiniMaxClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
