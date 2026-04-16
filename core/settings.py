import secrets
from datetime import timedelta
from functools import lru_cache
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    name: str = "MiniMax API Plan"
    version: str = "1.0.0"
    debug: bool = False
    allowed_origins: list[str] = ["*"]

    class Config:
        env_prefix = "APP_"
        extra = "ignore"


class MiniMaxSettings(BaseSettings):
    api_key: Optional[str] = None
    group_id: Optional[str] = None
    base_url: str = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    default_model: str = "abab6.5s-chat"
    timeout: float = 60.0

    @field_validator("api_key", mode="before")
    @classmethod
    def validate_api_key(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "your_api_key_here":
            return None
        return v

    class Config:
        env_prefix = "MINIMAX_"
        extra = "ignore"


class DatabaseSettings(BaseSettings):
    driver: str = "mysql+aiomysql"
    host: str = "localhost"
    port: int = 3306
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    charset: str = "utf8mb4"
    pool_size: int = 10
    max_overflow: int = 5
    pool_recycle: int = 3600
    echo: bool = False

    def get_dsn(self) -> str:
        if not all([self.driver, self.host, self.username, self.password, self.database]):
            return ""
        return (
            f"{self.driver}://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}?charset={self.charset}"
        )

    class Config:
        env_prefix = "DB_"
        extra = "ignore"


class EvaluationSettings(BaseSettings):
    enabled: bool = False
    model: str = "abab6.5s-chat"

    class Config:
        env_prefix = "EVALUATION_"
        extra = "ignore"


class JWTSettings(BaseSettings):
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    @property
    def access_token_expire_delta(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)

    class Config:
        env_prefix = "JWT_"
        extra = "ignore"


class Settings(BaseSettings):
    app: AppSettings = Field(default_factory=AppSettings)
    minimax: MiniMaxSettings = Field(default_factory=MiniMaxSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    evaluation: EvaluationSettings = Field(default_factory=EvaluationSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
