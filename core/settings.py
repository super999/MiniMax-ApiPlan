import secrets
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILES = [
    BASE_DIR / "public_env.data",
    BASE_DIR / ".env",
]
ENV_FILE_ENCODING = "utf-8"


class AppSettings(BaseSettings):
    name: str = "MiniMax API Plan"
    version: str = "1.0.0"
    debug: bool = False
    allowed_origins: list[str] = ["*"]

    class Config:
        env_prefix = "APP_"
        env_file = ENV_FILES
        env_file_encoding = ENV_FILE_ENCODING
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
        env_file = ENV_FILES
        env_file_encoding = ENV_FILE_ENCODING
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
        env_file = ENV_FILES
        env_file_encoding = ENV_FILE_ENCODING
        extra = "ignore"


class EvaluationSettings(BaseSettings):
    enabled: bool = False
    model: str = "abab6.5s-chat"

    class Config:
        env_prefix = "EVALUATION_"
        env_file = ENV_FILES
        env_file_encoding = ENV_FILE_ENCODING
        extra = "ignore"


class JWTSettings(BaseSettings):
    secret_key: str = "minimax_api_plan_default_jwt_secret_key_2024_secure_abc123xyz"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    @property
    def access_token_expire_delta(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)

    class Config:
        env_prefix = "JWT_"
        env_file = ENV_FILES
        env_file_encoding = ENV_FILE_ENCODING
        extra = "ignore"


class LogSettings(BaseSettings):
    level: str = "DEBUG"
    file_enabled: bool = True
    file_path: str = "logs/app.log"
    rotation_days: int = 7

    class Config:
        env_prefix = "LOG_"
        env_file = ENV_FILES
        env_file_encoding = ENV_FILE_ENCODING
        extra = "ignore"


class Settings(BaseSettings):
    app: AppSettings = Field(default_factory=AppSettings)
    minimax: MiniMaxSettings = Field(default_factory=MiniMaxSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    evaluation: EvaluationSettings = Field(default_factory=EvaluationSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    log: LogSettings = Field(default_factory=LogSettings)

    class Config:
        env_file = ENV_FILES
        env_file_encoding = ENV_FILE_ENCODING
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
