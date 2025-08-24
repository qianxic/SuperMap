"""
SuperMap GIS + AI Backend - FastAPI应用主入口
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.api.v1 import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 SuperMap Backend 正在启动...")
    print(f"📊 配置环境: {settings.environment}")
    print(f"🔐 JWT算法: {settings.algorithm}")
    yield
    # 关闭时执行
    print("🛑 SuperMap Backend 正在关闭...")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于多智能体协作的 GIS 智能分析平台后端API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.debug else None,
            "error_code": 500
        }
    )


# 根路径
@app.get("/", tags=["系统"])
async def root():
    """系统根路径"""
    return {
        "success": True,
        "message": "欢迎使用 SuperMap GIS + AI 智能分析系统",
        "version": settings.app_version,
        "docs": "/docs",
        "environment": settings.environment
    }


# 健康检查
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {
        "success": True,
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    }


# 注册API路由 - 使用统一的路由管理器
app.include_router(
    api_v1_router,
    prefix=settings.api_v1_prefix
)


# 开发环境启动
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )