from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typing import Any

from core.logger import get_logger
from core.settings import settings
from db.session import is_database_configured
from api.chat import get_minimax_client

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["health"])


@router.get(
    "/health",
    summary="健康检查",
    responses={
        200: {"description": "服务正常"},
        503: {"description": "服务不可用"},
    },
)
async def health_check(
    minimax_client: Any = Depends(get_minimax_client),
) -> JSONResponse:
    health_status = {
        "status": "healthy",
        "components": {
            "app": {"status": "healthy"},
            "minimax_api": {
                "status": "healthy" if minimax_client is not None else "unhealthy",
                "configured": minimax_client is not None,
            },
            "database": {
                "status": "healthy" if is_database_configured() else "unconfigured",
                "configured": is_database_configured(),
            },
        },
        "version": settings.app.version,
        "app_name": settings.app.name,
    }

    all_healthy = (
        health_status["components"]["app"]["status"] == "healthy"
        and health_status["components"]["minimax_api"]["status"] == "healthy"
    )

    return JSONResponse(
        content=health_status,
        status_code=status.HTTP_200_OK
        if all_healthy
        else status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@router.get(
    "/info",
    summary="服务信息",
)
async def get_info() -> dict[str, Any]:
    return {
        "name": settings.app.name,
        "version": settings.app.version,
        "status": "running",
        "features": [
            "MiniMax API 调用",
            "Pydantic 模型验证",
            "分层架构",
            "MySQL 数据库支持",
            "评测服务预留接口",
            "统一配置管理",
            "日志记录",
        ],
        "config": {
            "debug": settings.app.debug,
            "default_model": settings.minimax.default_model,
            "evaluation_enabled": settings.evaluation.enabled,
            "database_configured": is_database_configured(),
        },
    }
