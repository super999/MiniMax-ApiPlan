import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from api.chat import router as chat_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MiniMax API Plan 服务启动中...")
    logger.info(f"当前工作目录: {os.getcwd()}")
    yield
    logger.info("MiniMax API Plan 服务关闭中...")


app = FastAPI(
    title="MiniMax API Plan",
    description="基于 FastAPI 的 MiniMax API 调用服务，支持智能体代码评测",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    logger.warning(f"静态文件目录不存在: {static_dir}")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")
if os.path.exists(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)
else:
    logger.warning(f"模板目录不存在: {templates_dir}")
    templates = None


@app.get("/", response_class=HTMLResponse, summary="主页")
async def index(request: Request):
    if templates is None:
        return HTMLResponse(
            content="<h1>模板目录不存在，请检查 templates 文件夹</h1>",
            status_code=500
        )
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/info", summary="服务信息")
async def get_info():
    return {
        "name": "MiniMax API Plan",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "MiniMax API 调用",
            "Pydantic 模型验证",
            "分层架构",
            "评测服务预留接口",
            "日志记录"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
