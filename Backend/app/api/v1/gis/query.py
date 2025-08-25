"""
GIS空间查询API
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.application.use_cases.gis.query_use_case import GISQueryUseCase
from app.domains.gis.repositories import (
    LayerRepository, SpatialFeatureRepository, SpatialQueryRepository
)
from app.infrastructure.database.postgres.repositories import (
    PostgreSQLLayerRepository, PostgreSQLSpatialFeatureRepository
)

router = APIRouter()


# 请求模型
class ExtentQueryRequest(BaseModel):
    layer_id: str
    extent: Dict[str, Any]


class GeometryTypeQueryRequest(BaseModel):
    layer_id: str
    geometry_type: str


class DistanceQueryRequest(BaseModel):
    layer_id: str
    geometry_wkt: str
    distance: float


class SpatialQueryRequest(BaseModel):
    layer_id: str
    geometry_wkt: str


class ComplexQueryRequest(BaseModel):
    layer_id: str
    spatial_filter: Optional[Dict[str, Any]] = None
    attribute_filter: Optional[Dict[str, Any]] = None
    sql_query: Optional[str] = None
    limit: int = 1000
    offset: int = 0


# 临时 SpatialQueryRepository 实现
class TemporarySpatialQueryRepository(SpatialQueryRepository):
    """临时的空间查询仓储实现"""
    
    def __init__(self, session):
        self.session = session
    
    async def execute_spatial_query(self, query):
        return []
    
    async def execute_attribute_query(self, query):
        return []
    
    async def execute_sql_query(self, query):
        return []
    
    async def execute_hybrid_query(self, query):
        return []
    
    async def find_features_within_distance(self, layer_id, geometry, distance):
        return []
    
    async def find_features_intersecting(self, layer_id, geometry):
        return []
    
    async def find_features_containing(self, layer_id, geometry):
        return []
    
    async def find_features_within(self, layer_id, geometry):
        return []


# 依赖注入
def get_query_use_case(session = Depends(get_db)) -> GISQueryUseCase:
    """获取查询用例实例"""
    layer_repo = PostgreSQLLayerRepository(session)
    feature_repo = PostgreSQLSpatialFeatureRepository(session)
    query_repo = TemporarySpatialQueryRepository(session)
    
    return GISQueryUseCase(layer_repo, feature_repo, query_repo)


@router.post("/extent")
async def query_features_by_extent(
    request: ExtentQueryRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISQueryUseCase = Depends(get_query_use_case)
) -> Dict[str, Any]:
    """根据空间范围查询要素"""
    try:
        result = await use_case.query_features_by_extent(
            layer_id=request.layer_id,
            extent=request.extent
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"空间范围查询失败: {str(e)}"
        )


@router.post("/geometry-type")
async def query_features_by_geometry_type(
    request: GeometryTypeQueryRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISQueryUseCase = Depends(get_query_use_case)
) -> Dict[str, Any]:
    """根据几何类型查询要素"""
    try:
        result = await use_case.query_features_by_geometry_type(
            layer_id=request.layer_id,
            geometry_type=request.geometry_type
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"几何类型查询失败: {str(e)}"
        )


@router.post("/distance")
async def query_features_within_distance(
    request: DistanceQueryRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISQueryUseCase = Depends(get_query_use_case)
) -> Dict[str, Any]:
    """查询指定距离内的要素"""
    try:
        result = await use_case.query_features_within_distance(
            layer_id=request.layer_id,
            geometry_wkt=request.geometry_wkt,
            distance=request.distance
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"距离查询失败: {str(e)}"
        )


@router.post("/intersecting")
async def query_features_intersecting(
    request: SpatialQueryRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISQueryUseCase = Depends(get_query_use_case)
) -> Dict[str, Any]:
    """查询相交的要素"""
    try:
        result = await use_case.query_features_intersecting(
            layer_id=request.layer_id,
            geometry_wkt=request.geometry_wkt
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"相交查询失败: {str(e)}"
        )


@router.post("/containing")
async def query_features_containing(
    request: SpatialQueryRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISQueryUseCase = Depends(get_query_use_case)
) -> Dict[str, Any]:
    """查询包含指定几何的要素"""
    try:
        result = await use_case.query_features_containing(
            layer_id=request.layer_id,
            geometry_wkt=request.geometry_wkt
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"包含查询失败: {str(e)}"
        )


@router.post("/within")
async def query_features_within(
    request: SpatialQueryRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISQueryUseCase = Depends(get_query_use_case)
) -> Dict[str, Any]:
    """查询在指定几何内的要素"""
    try:
        result = await use_case.query_features_within(
            layer_id=request.layer_id,
            geometry_wkt=request.geometry_wkt
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内部查询失败: {str(e)}"
        )


@router.post("/spatial")
async def execute_spatial_query(
    request: ComplexQueryRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISQueryUseCase = Depends(get_query_use_case)
) -> Dict[str, Any]:
    """执行空间查询"""
    try:
        if not request.spatial_filter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="空间查询必须提供spatial_filter参数"
            )
        
        result = await use_case.execute_spatial_query(
            layer_id=request.layer_id,
            spatial_filter=request.spatial_filter,
            limit=request.limit,
            offset=request.offset
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"空间查询失败: {str(e)}"
        )


@router.post("/attribute")
async def execute_attribute_query(
    request: ComplexQueryRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISQueryUseCase = Depends(get_query_use_case)
) -> Dict[str, Any]:
    """执行属性查询"""
    try:
        if not request.attribute_filter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="属性查询必须提供attribute_filter参数"
            )
        
        result = await use_case.execute_attribute_query(
            layer_id=request.layer_id,
            attribute_filter=request.attribute_filter,
            limit=request.limit,
            offset=request.offset
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"属性查询失败: {str(e)}"
        )


@router.post("/sql")
async def execute_sql_query(
    request: ComplexQueryRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISQueryUseCase = Depends(get_query_use_case)
) -> Dict[str, Any]:
    """执行SQL查询"""
    try:
        if not request.sql_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SQL查询必须提供sql_query参数"
            )
        
        result = await use_case.execute_sql_query(
            layer_id=request.layer_id,
            sql_query=request.sql_query,
            limit=request.limit,
            offset=request.offset
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SQL查询失败: {str(e)}"
        )


@router.get("/layer/{layer_id}/features")
async def get_layer_features(
    layer_id: str,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(1000, ge=1, le=10000, description="返回记录数"),
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISQueryUseCase = Depends(get_query_use_case)
) -> Dict[str, Any]:
    """获取图层所有要素"""
    try:
        result = await use_case.get_layer_features(
            layer_id=layer_id,
            skip=skip,
            limit=limit
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图层要素失败: {str(e)}"
        )


@router.get("/layer/{layer_id}/statistics")
async def get_layer_statistics(
    layer_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """获取图层统计信息"""
    try:
        from app.domains.gis.services import LayerManagementService
        from app.infrastructure.database.postgres.repositories import PostgreSQLLayerRepository, PostgreSQLSpatialFeatureRepository
        
        layer_repo = PostgreSQLLayerRepository(session)
        feature_repo = PostgreSQLSpatialFeatureRepository(session)
        
        layer_service = LayerManagementService(layer_repo, feature_repo)
        stats = await layer_service.calculate_layer_statistics(UUID(layer_id))
        
        return {
            "success": True,
            "message": "获取图层统计信息成功",
            "data": {
                "layer_id": layer_id,
                "statistics": stats
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图层统计信息失败: {str(e)}"
        )