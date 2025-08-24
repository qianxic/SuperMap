"""
GIS空间分析API
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

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


# 请求模型
class BufferAnalysisRequest(BaseModel):
    layer_id: str
    distance: float
    geometry_id: Optional[str] = None
    geometry_wkt: Optional[str] = None


class DistanceAnalysisRequest(BaseModel):
    layer_id: str
    geometry1_id: str
    geometry2_id: str


class IntersectionAnalysisRequest(BaseModel):
    layer_id: str
    geometry1_id: str
    geometry2_id: str


class UnionAnalysisRequest(BaseModel):
    layer_id: str
    geometry_ids: List[str]


class AccessibilityAnalysisRequest(BaseModel):
    layer_id: str
    center_geometry_id: str
    max_distance: float


# 依赖注入
def get_analysis_use_case(session = Depends(get_db)) -> GISAnalysisUseCase:
    """获取分析用例实例"""
    layer_repo = PostgreSQLLayerRepository(session)
    feature_repo = PostgreSQLSpatialFeatureRepository(session)
    result_repo = PostgreSQLAnalysisResultRepository(session)
    
    return GISAnalysisUseCase(layer_repo, feature_repo, result_repo)


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
            detail=f"缓冲区分析失败: {str(e)}"
        )


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
            geometry2_id=request.geometry2_id
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
            geometry2_id=request.geometry2_id
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
            geometry_ids=request.geometry_ids
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
            center_geometry_id=request.center_geometry_id,
            max_distance=request.max_distance
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


@router.get("/result/{analysis_id}")
async def get_analysis_result(
    analysis_id: str,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISAnalysisUseCase = Depends(get_analysis_use_case)
) -> Dict[str, Any]:
    """获取分析结果"""
    try:
        result = await use_case.get_analysis_result(analysis_id)
        
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
            detail=f"获取分析结果失败: {str(e)}"
        )


@router.get("/results")
async def get_analysis_results(
    analysis_type: Optional[str] = Query(None, description="分析类型"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISAnalysisUseCase = Depends(get_analysis_use_case)
) -> Dict[str, Any]:
    """获取分析结果列表"""
    try:
        if analysis_type:
            result = await use_case.get_analysis_results_by_type(
                analysis_type, skip, limit
            )
        else:
            # 获取所有分析结果
            result = await use_case.get_analysis_results_by_type(
                "all", skip, limit
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
            detail=f"获取分析结果列表失败: {str(e)}"
        )


@router.delete("/result/{analysis_id}")
async def delete_analysis_result(
    analysis_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """删除分析结果"""
    try:
        result_repo = PostgreSQLAnalysisResultRepository(session)
        success = await result_repo.delete(analysis_id)
        
        if success:
            return {
                "success": True,
                "message": "分析结果删除成功",
                "data": {"analysis_id": analysis_id}
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分析结果不存在"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除分析结果失败: {str(e)}"
        )
