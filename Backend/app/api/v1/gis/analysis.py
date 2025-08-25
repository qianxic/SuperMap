"""
GIS空间分析API
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.application.use_cases.gis.analysis_use_case import GISAnalysisUseCase
from app.domains.gis.repositories import (
    LayerRepository, SpatialFeatureRepository, AnalysisResultRepository
)
from app.infrastructure.database.postgres.repositories import (
    PostgreSQLLayerRepository, PostgreSQLSpatialFeatureRepository, 
    PostgreSQLAnalysisResultRepository
)

router = APIRouter()


# ==================== 请求模型 ====================

class BufferAnalysisRequest(BaseModel):
    """缓冲区分析请求"""
    layer_id: str = Field(..., description="图层ID")
    distance: float = Field(..., gt=0, description="缓冲区距离(米)")
    geometry_id: Optional[str] = Field(None, description="几何要素ID")
    geometry_wkt: Optional[str] = Field(None, description="几何要素WKT字符串")
    
    @validator('distance')
    def validate_distance(cls, v):
        if v <= 0:
            raise ValueError('缓冲区距离必须大于0')
        return v


class PathPlanningRequest(BaseModel):
    """路径规划请求"""
    layer_id: str = Field(..., description="图层ID")
    start_point: Dict[str, Any] = Field(..., description="起始点坐标")
    end_point: Dict[str, Any] = Field(..., description="目标点坐标")
    path_type: str = Field("最短路径", description="路径类型")
    transport_mode: str = Field("步行", description="交通方式")
    
    @validator('path_type')
    def validate_path_type(cls, v):
        allowed_types = ["最短路径", "最快路径", "最少转弯", "避开拥堵"]
        if v not in allowed_types:
            raise ValueError(f'路径类型必须是: {", ".join(allowed_types)}')
        return v
    
    @validator('transport_mode')
    def validate_transport_mode(cls, v):
        allowed_modes = ["步行", "驾车", "公交", "骑行"]
        if v not in allowed_modes:
            raise ValueError(f'交通方式必须是: {", ".join(allowed_modes)}')
        return v


class AccessibilityAnalysisRequest(BaseModel):
    """可达性分析请求"""
    layer_id: str = Field(..., description="图层ID")
    center_point: Dict[str, Any] = Field(..., description="分析中心点坐标")
    max_distance: float = Field(..., gt=0, description="最大距离(米)")
    transport_mode: str = Field("步行", description="交通方式")
    
    @validator('max_distance')
    def validate_max_distance(cls, v):
        if v <= 0:
            raise ValueError('最大距离必须大于0')
        return v
    
    @validator('transport_mode')
    def validate_transport_mode(cls, v):
        allowed_modes = ["步行", "驾车", "公交", "骑行"]
        if v not in allowed_modes:
            raise ValueError(f'交通方式必须是: {", ".join(allowed_modes)}')
        return v


class DistanceAnalysisRequest(BaseModel):
    """距离分析请求"""
    layer_id: str = Field(..., description="图层ID")
    geometry1_id: str = Field(..., description="第一个几何要素ID")
    geometry2_id: str = Field(..., description="第二个几何要素ID")


class IntersectionAnalysisRequest(BaseModel):
    """相交分析请求"""
    layer_id: str = Field(..., description="图层ID")
    geometry1_id: str = Field(..., description="第一个几何要素ID")
    geometry2_id: str = Field(..., description="第二个几何要素ID")


class UnionAnalysisRequest(BaseModel):
    """合并分析请求"""
    layer_id: str = Field(..., description="图层ID")
    geometry_ids: List[str] = Field(..., description="要合并的几何要素ID列表")
    
    @validator('geometry_ids')
    def validate_geometry_ids(cls, v):
        if len(v) < 2:
            raise ValueError('至少需要2个几何要素进行合并')
        return v


# ==================== 依赖注入 ====================

def get_analysis_use_case(session = Depends(get_db)) -> GISAnalysisUseCase:
    """获取分析用例实例"""
    layer_repo = PostgreSQLLayerRepository(session)
    feature_repo = PostgreSQLSpatialFeatureRepository(session)
    result_repo = PostgreSQLAnalysisResultRepository(session)
    
    return GISAnalysisUseCase(layer_repo, feature_repo, result_repo)


# ==================== 缓冲区分析 ====================

@router.post("/buffer")
async def buffer_analysis(
    request: BufferAnalysisRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISAnalysisUseCase = Depends(get_analysis_use_case)
) -> Dict[str, Any]:
    """缓冲区分析"""
    try:
        result = await use_case.perform_buffer_analysis(
            layer_id=request.layer_id,
            distance=request.distance,
            geometry_id=request.geometry_id,
            geometry_wkt=request.geometry_wkt,
            user_id=current_user_id
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
            detail=f"缓冲区分析失败: {str(e)}"
        )


# ==================== 路径规划 ====================

@router.post("/path-planning")
async def path_planning(
    request: PathPlanningRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISAnalysisUseCase = Depends(get_analysis_use_case)
) -> Dict[str, Any]:
    """路径规划分析"""
    try:
        result = await use_case.perform_path_planning(
            layer_id=request.layer_id,
            start_point=request.start_point,
            end_point=request.end_point,
            path_type=request.path_type,
            transport_mode=request.transport_mode,
            user_id=current_user_id
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
            detail=f"路径规划失败: {str(e)}"
        )


# ==================== 可达性分析 ====================

@router.post("/accessibility")
async def accessibility_analysis(
    request: AccessibilityAnalysisRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISAnalysisUseCase = Depends(get_analysis_use_case)
) -> Dict[str, Any]:
    """可达性分析"""
    try:
        result = await use_case.perform_accessibility_analysis(
            layer_id=request.layer_id,
            center_point=request.center_point,
            max_distance=request.max_distance,
            transport_mode=request.transport_mode,
            user_id=current_user_id
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
            detail=f"可达性分析失败: {str(e)}"
        )


# ==================== 其他分析功能 ====================

@router.post("/distance")
async def distance_analysis(
    request: DistanceAnalysisRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISAnalysisUseCase = Depends(get_analysis_use_case)
) -> Dict[str, Any]:
    """距离分析"""
    try:
        result = await use_case.perform_distance_analysis(
            layer_id=request.layer_id,
            geometry1_id=request.geometry1_id,
            geometry2_id=request.geometry2_id,
            user_id=current_user_id
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
            detail=f"距离分析失败: {str(e)}"
        )


@router.post("/intersection")
async def intersection_analysis(
    request: IntersectionAnalysisRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISAnalysisUseCase = Depends(get_analysis_use_case)
) -> Dict[str, Any]:
    """相交分析"""
    try:
        result = await use_case.perform_intersection_analysis(
            layer_id=request.layer_id,
            geometry1_id=request.geometry1_id,
            geometry2_id=request.geometry2_id,
            user_id=current_user_id
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
            detail=f"相交分析失败: {str(e)}"
        )


@router.post("/union")
async def union_analysis(
    request: UnionAnalysisRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISAnalysisUseCase = Depends(get_analysis_use_case)
) -> Dict[str, Any]:
    """合并分析"""
    try:
        result = await use_case.perform_union_analysis(
            layer_id=request.layer_id,
            geometry_ids=request.geometry_ids,
            user_id=current_user_id
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
            detail=f"合并分析失败: {str(e)}"
        )


# ==================== 分析结果管理 ====================

@router.get("/results")
async def get_analysis_results(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    analysis_type: Optional[str] = Query(None, description="分析类型过滤"),
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISAnalysisUseCase = Depends(get_analysis_use_case)
) -> Dict[str, Any]:
    """获取分析结果列表"""
    try:
        result = await use_case.get_analysis_results(
            user_id=current_user_id,
            skip=skip,
            limit=limit,
            analysis_type=analysis_type
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
            detail=f"获取分析结果失败: {str(e)}"
        )


@router.get("/results/{result_id}")
async def get_analysis_result_by_id(
    result_id: str,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISAnalysisUseCase = Depends(get_analysis_use_case)
) -> Dict[str, Any]:
    """根据ID获取分析结果详情"""
    try:
        result = await use_case.get_analysis_result_by_id(
            result_id=result_id,
            user_id=current_user_id
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析结果详情失败: {str(e)}"
        )


@router.delete("/results/{result_id}")
async def delete_analysis_result(
    result_id: str,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISAnalysisUseCase = Depends(get_analysis_use_case)
) -> Dict[str, Any]:
    """删除分析结果"""
    try:
        result = await use_case.delete_analysis_result(
            result_id=result_id,
            user_id=current_user_id
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
            detail=f"删除分析结果失败: {str(e)}"
        )
