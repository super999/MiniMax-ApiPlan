import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.logger import setup_logger, get_logger
from core.settings import settings
from db.session import create_tables, close_db_pool, is_database_configured
from api.chat import router as chat_router
from api.health import router as health_router
from api.auth import router as auth_router
from api.project import router as project_router
from api.script_work import router as script_work_router
from api.script_generation import router as script_generation_router

logger = setup_logger()
app_logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

templates = None
if TEMPLATES_DIR.exists():
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
else:
    app_logger.warning(f"模板目录不存在: {TEMPLATES_DIR}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info(f"===== {settings.app.name} 服务启动中 =====")
    app_logger.info(f"版本: {settings.app.version}")
    app_logger.info(f"工作目录: {os.getcwd()}")

    if is_database_configured():
        app_logger.info("数据库已配置，准备初始化...")
        try:
            await create_tables()
            app_logger.info("数据库初始化完成")
        except Exception as e:
            app_logger.error(f"数据库初始化失败: {e}", exc_info=True)
    else:
        app_logger.info("数据库未配置，跳过数据库初始化")

    app_logger.info("===== 服务启动完成 =====")

    yield

    app_logger.info("===== 服务关闭中 =====")

    if is_database_configured():
        app_logger.info("关闭数据库连接池...")
        try:
            await close_db_pool()
            app_logger.info("数据库连接池已关闭")
        except Exception as e:
            app_logger.error(f"关闭数据库连接池失败: {e}")

    app_logger.info("===== 服务已关闭 =====")


app = FastAPI(
    title=settings.app.name,
    description="基于 FastAPI 的 MiniMax API 调用服务，支持智能体代码评测",
    version=settings.app.version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(script_work_router)
app.include_router(script_generation_router)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
else:
    app_logger.warning(f"静态文件目录不存在: {STATIC_DIR}")


@app.get("/", response_class=HTMLResponse, summary="主页")
async def index(request: Request):
    if templates is None:
        return HTMLResponse(
            content="<h1>模板目录不存在，请检查 templates 文件夹</h1>",
            status_code=500,
        )
    return templates.TemplateResponse(request=request, name="index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app.debug,
    )
