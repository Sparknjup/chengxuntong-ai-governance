"""
城讯通后端系统 - 启动入口
"""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.core.database import engine, Base
from app.core.logger import logger
from app.core.exceptions import register_exception_handlers
from app.api import users, orders, points, departments, admins, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info(f"🚀 {settings.APP_NAME} 启动中...")
    logger.info(f"环境: {settings.APP_ENV} | Debug: {settings.DEBUG}")

    # 自动建表（如果不存在）
    Base.metadata.create_all(bind=engine)
    logger.info("数据表检查完成")

    # 确保上传目录存在
    Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
    Path(settings.LOG_DIR).mkdir(exist_ok=True)

    yield

    # 关闭
    logger.info("🛑 应用关闭")


app = FastAPI(
    title=settings.APP_NAME,
    description="城讯通城市问题上报平台后端 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} "
        f"-> {response.status_code} ({duration}ms)"
    )
    return response


# 统一异常处理
register_exception_handlers(app)


# 静态文件（访问上传的图片等）
if Path(settings.UPLOAD_DIR).exists():
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# 路由注册
app.include_router(users.router, prefix="/api/users", tags=["用户模块"])
app.include_router(orders.router, prefix="/api/orders", tags=["工单模块"])
app.include_router(points.router, prefix="/api/points", tags=["积分模块"])
app.include_router(departments.router, prefix="/api/departments", tags=["部门模块"])
app.include_router(admins.router, prefix="/api/admins", tags=["管理员模块"])
app.include_router(stats.router, prefix="/api/stats", tags=["统计模块"])


# Web 前端（只暴露明确列出的静态文件，避免泄露 .env 等项目文件）
WEB_ROOT = Path(__file__).resolve().parent


@app.get("/web", include_in_schema=False)
def web_home():
    return RedirectResponse(url="/chengxuntong-home.html")


@app.get("/chengxuntong-home.html", include_in_schema=False)
def website_page():
    return FileResponse(WEB_ROOT / "chengxuntong-home.html")


@app.get("/index.html", include_in_schema=False)
def workbench_page():
    return FileResponse(WEB_ROOT / "index.html")


@app.get("/home-api.js", include_in_schema=False)
def website_script():
    return FileResponse(WEB_ROOT / "home-api.js", media_type="text/javascript")


@app.get("/index-api.js", include_in_schema=False)
def workbench_script():
    return FileResponse(WEB_ROOT / "index-api.js", media_type="text/javascript")


@app.get("/chengxuntong-reference.png", include_in_schema=False)
def website_reference_image():
    return FileResponse(WEB_ROOT / "chengxuntong-reference.png")


@app.get("/", tags=["系统"])
def root():
    return {
        "success": True,
        "message": f"{settings.APP_NAME} v1.0.0 运行中 ✅",
        "docs": "/docs"
    }


@app.get("/health", tags=["系统"])
def health():
    """健康检查"""
    return {"success": True, "status": "ok", "timestamp": int(time.time())}
