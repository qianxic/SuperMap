"""
GIS模块路由管理器
统一管理GIS相关的所有API路由
"""
from fastapi import APIRouter

# 导入子模块路由
from .analysis import router as analysis_router
from .query import router as query_router
from .layer import router as layer_router

# 创建GIS主路由
gis_router = APIRouter()

# 注册子模块路由
gis_router.include_router(layer_router, prefix="/layer", tags=["图层管理"])
gis_router.include_router(analysis_router, prefix="/analysis", tags=["空间分析"])
gis_router.include_router(query_router, prefix="/query", tags=["空间查询"])

# 导出主路由
__all__ = ["gis_router"]
