from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class MiniMaxMessage(BaseModel):
    role: str = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")


class MiniMaxUsage(BaseModel):
    total_tokens: int = Field(default=0, description="总token数")
    prompt_tokens: int = Field(default=0, description="输入token数")
    completion_tokens: int = Field(default=0, description="输出token数")


class MiniMaxResponse(BaseModel):
    id: Optional[str] = Field(default=None, description="请求ID")
    created: Optional[int] = Field(default=None, description="创建时间戳")
    model: Optional[str] = Field(default=None, description="使用的模型")
    choices: Optional[List[Any]] = Field(default=None, description="模型生成的选择")
    usage: Optional[MiniMaxUsage] = Field(default=None, description="token使用情况")

    def get_content(self) -> str:
        if self.choices and len(self.choices) > 0:
            message = self.choices[0].get("message", {}) if isinstance(self.choices[0], dict) else {}
            return message.get("content", "")
        return ""


class ChatResponse(BaseModel):
    success: bool = Field(..., description="请求是否成功")
    content: Optional[str] = Field(default=None, description="模型返回的内容")
    model: Optional[str] = Field(default=None, description="使用的模型")
    usage: Optional[MiniMaxUsage] = Field(default=None, description="token使用情况")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    latency_ms: Optional[float] = Field(default=None, description="请求耗时（毫秒）")
    error_msg: Optional[str] = Field(default=None, description="错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "content": "你好！我是MiniMax的AI助手，很高兴为您服务。",
                "model": "abab6.5s-chat",
                "usage": {"total_tokens": 50, "prompt_tokens": 10, "completion_tokens": 40},
                "request_id": "chatcmpl-12345",
                "latency_ms": 1500.5,
                "error_msg": None,
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class EvaluationResult(BaseModel):
    score: Optional[float] = Field(default=None, description="评测分数")
    passed: Optional[bool] = Field(default=None, description="是否通过评测")
    details: Optional[dict] = Field(default=None, description="评测详情")
    error: Optional[str] = Field(default=None, description="评测错误信息")
