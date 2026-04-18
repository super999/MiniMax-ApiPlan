import time
from dataclasses import dataclass
from typing import Any, Optional
import httpx

from core.settings import settings, MiniMaxSettings
from core.logger import get_logger

logger = get_logger(__name__)


def _mask_api_key(key: Optional[str]) -> str:
    if not key:
        return "None"
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


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
        self._log_config()

    def _log_config(self) -> None:
        masked_api_key = _mask_api_key(self._settings.api_key)
        logger.info(
            f"MiniMaxClient 配置: "
            f"base_url={self._settings.base_url}, "
            f"default_model={self._settings.default_model}, "
            f"timeout={self._settings.timeout}s, "
            f"api_key={masked_api_key}, "
            f"group_id={self._settings.group_id or '未配置'}"
        )

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

            full_url = self.base_url
            if params:
                query_str = "&".join([f"{k}={v}" for k, v in params.items()])
                full_url = f"{self.base_url}?{query_str}"

            logger.info(f"===== MiniMax API 请求开始 =====")
            logger.info(f"请求 URL: {full_url}")
            logger.info(f"请求方法: POST")
            logger.info(f"模型: {body.get('model')}")
            logger.info(f"Temperature: {body.get('temperature')}")
            logger.info(f"Max Tokens: {body.get('max_tokens')}")
            logger.info(f"Prompt 长度: {len(prompt)} 字符")
            logger.debug(f"完整请求体: {body}")

            response = await client.post(
                self.base_url,
                json=body,
                headers=headers,
                params=params,
            )

            latency_ms = (time.time() - start_time) * 1000

            logger.info(f"HTTP 状态码: {response.status_code}")
            logger.info(f"请求耗时: {latency_ms:.2f}ms")

            if response.status_code != 200:
                error_msg = f"API请求失败，状态码: {response.status_code}"
                response_text = response.text
                logger.error(f"{error_msg}")
                logger.error(f"原始响应: {response_text[:1000] if response_text else '空响应'}")

                try:
                    error_data = response.json()
                    logger.error(f"解析后的错误数据: {error_data}")
                except Exception:
                    error_data = {"detail": response_text}

                return (
                    None,
                    MiniMaxError(
                        code=response.status_code,
                        message=error_msg,
                        raw_error=error_data,
                    ),
                    latency_ms,
                )

            response_text = response.text
            logger.debug(f"原始响应内容: {response_text[:2000] if response_text else '空响应'}")

            try:
                response_data = response.json()
            except Exception as e:
                error_msg = f"解析响应JSON失败: {str(e)}"
                logger.error(f"{error_msg}")
                logger.error(f"响应文本: {response_text[:500] if response_text else '空'}")
                return (
                    None,
                    MiniMaxError(code=500, message=error_msg),
                    latency_ms,
                )

            result = self._parse_response(response_data)

            logger.info(f"响应 ID: {result.id or '无'}")
            logger.info(f"响应模型: {result.model or '无'}")
            logger.info(f"响应内容长度: {len(result.content)} 字符")
            if result.usage:
                logger.info(
                    f"Token 使用量: total={result.usage.total_tokens}, "
                    f"prompt={result.usage.prompt_tokens}, "
                    f"completion={result.usage.completion_tokens}"
                )
            logger.info(f"===== MiniMax API 请求成功 =====")

            return result, None, latency_ms

        except httpx.TimeoutException:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"===== MiniMax API 请求超时 =====")
            logger.error(f"超时时间配置: {self.timeout}s")
            logger.error(f"实际耗时: {latency_ms:.2f}ms")
            logger.error(f"请求 URL: {self.base_url}")
            logger.error(f"==================================")
            return (
                None,
                MiniMaxError(code=408, message=f"请求超时（配置: {self.timeout}s，实际: {latency_ms:.1f}ms），请稍后重试"),
                latency_ms,
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"===== MiniMax API 调用异常 =====")
            logger.error(f"异常类型: {type(e).__name__}")
            logger.error(f"异常信息: {str(e)}")
            logger.error(f"请求 URL: {self.base_url}")
            logger.error(f"==================================", exc_info=True)
            return (
                None,
                MiniMaxError(code=500, message=f"发生错误: {str(e)}"),
                latency_ms,
            )

    async def close(self) -> None:
        if self._owns_client and self._http_client is not None:
            logger.info("关闭 MiniMaxClient HTTP 连接")
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self) -> "MiniMaxClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
