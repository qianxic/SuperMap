"""
GIS领域 - 仓储接口定义
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from .entities import (
    SpatialFeature, Layer, AnalysisResult, SpatialQuery,
    SpatialExtent, GeometryType, AnalysisType
)
from shapely.geometry.base import BaseGeometry


class LayerRepository(ABC):
    """图层仓储接口"""
    
    @abstractmethod
    async def create(self, layer: Layer) -> Layer:
        """创建图层"""
        pass
    
    @abstractmethod
    async def get_by_id(self, layer_id: UUID) -> Optional[Layer]:
        """根据ID获取图层"""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Layer]:
        """根据名称获取图层"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Layer]:
        """获取所有图层"""
        pass
    
    @abstractmethod
    async def update(self, layer: Layer) -> Layer:
        """更新图层"""
        pass
    
    @abstractmethod
    async def delete(self, layer_id: UUID) -> bool:
        """删除图层"""
        pass
    
    @abstractmethod
    async def update_extent(self, layer_id: UUID, extent: SpatialExtent) -> bool:
        """更新图层空间范围"""
        pass
    
    @abstractmethod
    async def update_feature_count(self, layer_id: UUID, count: int) -> bool:
        """更新图层要素数量"""
        pass


class SpatialFeatureRepository(ABC):
    """空间要素仓储接口"""
    
    @abstractmethod
    async def create(self, feature: SpatialFeature) -> SpatialFeature:
        """创建空间要素"""
        pass
    
    @abstractmethod
    async def get_by_id(self, feature_id: UUID) -> Optional[SpatialFeature]:
        """根据ID获取空间要素"""
        pass
    
    @abstractmethod
    async def get_by_layer_id(self, layer_id: UUID, skip: int = 0, limit: int = 1000) -> List[SpatialFeature]:
        """根据图层ID获取空间要素"""
        pass
    
    @abstractmethod
    async def get_by_extent(self, layer_id: UUID, extent: SpatialExtent) -> List[SpatialFeature]:
        """根据空间范围获取要素"""
        pass
    
    @abstractmethod
    async def get_by_geometry_type(self, layer_id: UUID, geometry_type: GeometryType) -> List[SpatialFeature]:
        """根据几何类型获取要素"""
        pass
    
    @abstractmethod
    async def update(self, feature: SpatialFeature) -> SpatialFeature:
        """更新空间要素"""
        pass
    
    @abstractmethod
    async def delete(self, feature_id: UUID) -> bool:
        """删除空间要素"""
        pass
    
    @abstractmethod
    async def delete_by_layer_id(self, layer_id: UUID) -> bool:
        """删除图层的所有要素"""
        pass
    
    @abstractmethod
    async def count_by_layer_id(self, layer_id: UUID) -> int:
        """统计图层要素数量"""
        pass
    
    @abstractmethod
    async def get_extent_by_layer_id(self, layer_id: UUID) -> Optional[SpatialExtent]:
        """获取图层空间范围"""
        pass


class AnalysisResultRepository(ABC):
    """分析结果仓储接口"""
    
    @abstractmethod
    async def create(self, result: AnalysisResult) -> AnalysisResult:
        """创建分析结果"""
        pass
    
    @abstractmethod
    async def get_by_id(self, result_id: UUID) -> Optional[AnalysisResult]:
        """根据ID获取分析结果"""
        pass
    
    @abstractmethod
    async def get_by_analysis_type(self, analysis_type: AnalysisType, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """根据分析类型获取结果"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """获取所有分析结果"""
        pass
    
    @abstractmethod
    async def delete(self, result_id: UUID) -> bool:
        """删除分析结果"""
        pass
    
    @abstractmethod
    async def delete_by_analysis_type(self, analysis_type: AnalysisType) -> bool:
        """删除指定类型的分析结果"""
        pass


class SpatialQueryRepository(ABC):
    """空间查询仓储接口"""
    
    @abstractmethod
    async def execute_spatial_query(self, query: SpatialQuery) -> List[SpatialFeature]:
        """执行空间查询"""
        pass
    
    @abstractmethod
    async def execute_attribute_query(self, query: SpatialQuery) -> List[SpatialFeature]:
        """执行属性查询"""
        pass
    
    @abstractmethod
    async def execute_sql_query(self, query: SpatialQuery) -> List[Dict[str, Any]]:
        """执行SQL查询"""
        pass
    
    @abstractmethod
    async def execute_hybrid_query(self, query: SpatialQuery) -> List[SpatialFeature]:
        """执行混合查询"""
        pass
    
    @abstractmethod
    async def find_features_within_distance(
        self,
        layer_id: UUID,
        geometry: BaseGeometry,
        distance: float
    ) -> List[SpatialFeature]:
        """查找指定距离内的要素"""
        pass
    
    @abstractmethod
    async def find_features_intersecting(
        self,
        layer_id: UUID,
        geometry: BaseGeometry
    ) -> List[SpatialFeature]:
        """查找相交的要素"""
        pass
    
    @abstractmethod
    async def find_features_containing(
        self,
        layer_id: UUID,
        geometry: BaseGeometry
    ) -> List[SpatialFeature]:
        """查找包含指定几何的要素"""
        pass
    
    @abstractmethod
    async def find_features_within(
        self,
        layer_id: UUID,
        geometry: BaseGeometry
    ) -> List[SpatialFeature]:
        """查找在指定几何内的要素"""
        pass