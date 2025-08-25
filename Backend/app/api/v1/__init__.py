"""
API v1 版本路由管理器
统一管理所有功能模块的路由分组
"""
from fastapi import APIRouter

from app.api.v1.user.auth import router as user_auth_router
from app.api.v1.user.profile import router as user_profile_router
from app.api.v1.gis.analysis import router as gis_analysis_router
from app.api.v1.gis.query import router as gis_query_router
from app.api.v1.gis.layers import router as gis_layers_router

# 创建主路由
api_v1_router = APIRouter()

# 用户认证模块路由组
user_router = APIRouter(prefix="/user", tags=["用户认证"])
user_router.include_router(user_auth_router)
user_router.include_router(user_profile_router)

# GIS模块路由组
gis_router = APIRouter(prefix="/gis", tags=["GIS功能"])
gis_router.include_router(gis_layers_router, prefix="/layers", tags=["图层管理"])
gis_router.include_router(gis_analysis_router, prefix="/analysis", tags=["空间分析"])
gis_router.include_router(gis_query_router, prefix="/query", tags=["空间查询"])

# 注册路由
api_v1_router.include_router(user_router)
api_v1_router.include_router(gis_router)

# GIS分析模块路由组
from app.api.v1.gis import gis_router

# 注册GIS模块路由
api_v1_router.include_router(gis_router)

# TODO: 后续添加其他模块路由
# agent_router = APIRouter(prefix="/agent", tags=["智能体"])
# knowledge_router = APIRouter(prefix="/knowledge", tags=["知识库"])
# system_router = APIRouter(prefix="/system", tags=["系统管理"])
