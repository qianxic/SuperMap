"""
GIS分析用例
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry

from app.domains.gis.services import SpatialAnalysisService
from app.domains.gis.entities import AnalysisType, GeometryType
from app.domains.gis.repositories import (
    LayerRepository, SpatialFeatureRepository, AnalysisResultRepository
)


class GISAnalysisUseCase:
    """GIS分析用例"""
    
    def __init__(
        self,
        layer_repository: LayerRepository,
        feature_repository: SpatialFeatureRepository,
        result_repository: AnalysisResultRepository
    ):
        self.analysis_service = SpatialAnalysisService(
            layer_repository, feature_repository, result_repository
        )
        self.layer_repository = layer_repository
        self.feature_repository = feature_repository
    
    async def perform_buffer_analysis(
        self,
        layer_id: str,
        distance: float,
        geometry_id: Optional[str] = None,
        geometry_wkt: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行缓冲区分析"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 执行分析
            result = await self.analysis_service.buffer_analysis(
                layer_id=UUID(layer_id),
                distance=distance,
                geometry_id=UUID(geometry_id) if geometry_id else None,
                geometry_wkt=geometry_wkt
            )
            
            return {
                "success": True,
                "message": "缓冲区分析完成",
                "data": {
                    "analysis_id": str(result.id),
                    "analysis_type": result.analysis_type.value,
                    "result": result.result_data,
                    "statistics": result.statistics,
                    "execution_time": result.execution_time
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"缓冲区分析失败: {str(e)}",
                "data": None
            }
    
    async def perform_distance_analysis(
        self,
        layer_id: str,
        geometry1_id: str,
        geometry2_id: str
    ) -> Dict[str, Any]:
        """执行距离分析"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 执行分析
            result = await self.analysis_service.distance_analysis(
                layer_id=UUID(layer_id),
                geometry1_id=UUID(geometry1_id),
                geometry2_id=UUID(geometry2_id)
            )
            
            return {
                "success": True,
                "message": "距离分析完成",
                "data": {
                    "analysis_id": str(result.id),
                    "analysis_type": result.analysis_type.value,
                    "result": result.result_data,
                    "statistics": result.statistics,
                    "execution_time": result.execution_time
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"距离分析失败: {str(e)}",
                "data": None
            }
    
    async def perform_intersection_analysis(
        self,
        layer_id: str,
        geometry1_id: str,
        geometry2_id: str
    ) -> Dict[str, Any]:
        """执行相交分析"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 执行分析
            result = await self.analysis_service.intersection_analysis(
                layer_id=UUID(layer_id),
                geometry1_id=UUID(geometry1_id),
                geometry2_id=UUID(geometry2_id)
            )
            
            return {
                "success": True,
                "message": "相交分析完成",
                "data": {
                    "analysis_id": str(result.id),
                    "analysis_type": result.analysis_type.value,
                    "result": result.result_data,
                    "statistics": result.statistics,
                    "execution_time": result.execution_time
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"相交分析失败: {str(e)}",
                "data": None
            }
    
    async def perform_union_analysis(
        self,
        layer_id: str,
        geometry_ids: List[str]
    ) -> Dict[str, Any]:
        """执行合并分析"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 转换UUID列表
            geom_uuid_list = [UUID(gid) for gid in geometry_ids]
            
            # 执行分析
            result = await self.analysis_service.union_analysis(
                layer_id=UUID(layer_id),
                geometry_ids=geom_uuid_list
            )
            
            return {
                "success": True,
                "message": "合并分析完成",
                "data": {
                    "analysis_id": str(result.id),
                    "analysis_type": result.analysis_type.value,
                    "result": result.result_data,
                    "statistics": result.statistics,
                    "execution_time": result.execution_time
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"合并分析失败: {str(e)}",
                "data": None
            }
    
    async def perform_accessibility_analysis(
        self,
        layer_id: str,
        center_geometry_id: str,
        max_distance: float
    ) -> Dict[str, Any]:
        """执行可达性分析"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 执行分析
            result = await self.analysis_service.accessibility_analysis(
                layer_id=UUID(layer_id),
                center_geometry_id=UUID(center_geometry_id),
                max_distance=max_distance
            )
            
            return {
                "success": True,
                "message": "可达性分析完成",
                "data": {
                    "analysis_id": str(result.id),
                    "analysis_type": result.analysis_type.value,
                    "result": result.result_data,
                    "statistics": result.statistics,
                    "execution_time": result.execution_time
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"可达性分析失败: {str(e)}",
                "data": None
            }
    
    async def get_analysis_result(self, analysis_id: str) -> Dict[str, Any]:
        """获取分析结果"""
        try:
            result = await self.result_repository.get_by_id(UUID(analysis_id))
            if not result:
                raise ValueError(f"分析结果不存在: {analysis_id}")
            
            return {
                "success": True,
                "message": "获取分析结果成功",
                "data": result.to_dict()
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"获取分析结果失败: {str(e)}",
                "data": None
            }
    
    async def get_analysis_results_by_type(
        self,
        analysis_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """根据类型获取分析结果列表"""
        try:
            # 验证分析类型
            try:
                analysis_type_enum = AnalysisType(analysis_type)
            except ValueError:
                raise ValueError(f"不支持的分析类型: {analysis_type}")
            
            results = await self.result_repository.get_by_analysis_type(
                analysis_type_enum, skip, limit
            )
            
            return {
                "success": True,
                "message": "获取分析结果列表成功",
                "data": {
                    "results": [result.to_dict() for result in results],
                    "total": len(results),
                    "skip": skip,
                    "limit": limit
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"获取分析结果列表失败: {str(e)}",
                "data": None
            }