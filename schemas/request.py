from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="用户输入的提示词", min_length=1, max_length=10000)
    model: Optional[str] = Field(default="abab6.5s-chat", description="使用的模型名称")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="采样温度")
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=8192, description="最大生成token数")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "你好，请介绍一下你自己",
                "model": "abab6.5s-chat",
                "temperature": 0.7,
                "max_tokens": 2048
            }
        }
