"""
GIS模块路由管理器
统一管理GIS相关的所有API路由
"""
from fastapi import APIRouter

# 仅导入空间分析子模块
from .analysis import router as analysis_router

# 创建GIS主路由
gis_router = APIRouter()

# 注册分析路由
gis_router.include_router(analysis_router, prefix="/analysis", tags=["空间分析"])

# 导出主路由
__all__ = ["gis_router"]
