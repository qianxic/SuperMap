"""
GIS领域 - 领域服务
"""
import time
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from shapely.geometry import Point, LineString, Polygon, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shapely.affinity import scale, rotate, translate
import math
from datetime import datetime

from .entities import (
    SpatialFeature, Layer, AnalysisResult, SpatialQuery,
    SpatialExtent, GeometryType, AnalysisType, QueryType
)
from .repositories import (
    LayerRepository, SpatialFeatureRepository, 
    AnalysisResultRepository, SpatialQueryRepository
)


class SpatialAnalysisService:
    """空间分析服务"""
    
    def __init__(
        self,
        layer_repository: LayerRepository,
        feature_repository: SpatialFeatureRepository,
        result_repository: AnalysisResultRepository
    ):
        self.layer_repository = layer_repository
        self.feature_repository = feature_repository
        self.result_repository = result_repository
    
    async def buffer_analysis(
        self,
        layer_id: UUID,
        distance: float,
        geometry_id: Optional[UUID] = None,
        geometry_wkt: Optional[str] = None
    ) -> AnalysisResult:
        """缓冲区分析"""
        start_time = time.time()
        
        # 获取输入几何
        if geometry_id:
            feature = await self.feature_repository.get_by_id(geometry_id)
            if not feature:
                raise ValueError(f"要素不存在: {geometry_id}")
            input_geometry = feature.geometry
        elif geometry_wkt:
            input_geometry = shape(geometry_wkt)
        else:
            raise ValueError("必须提供几何ID或WKT几何")
        
        # 执行缓冲区分析
        buffer_geometry = input_geometry.buffer(distance)
        
        # 计算统计信息
        area = buffer_geometry.area
        perimeter = buffer_geometry.length if hasattr(buffer_geometry, 'length') else 0
        
        result_data = {
            "buffer_geometry": buffer_geometry.wkt,
            "area": area,
            "perimeter": perimeter,
            "distance": distance
        }
        
        statistics = {
            "area": area,
            "perimeter": perimeter,
            "distance": distance
        }
        
        execution_time = time.time() - start_time
        
        # 创建分析结果
        result = AnalysisResult.create_new(
            analysis_type=AnalysisType.BUFFER,
            input_parameters={
                "layer_id": str(layer_id),
                "geometry_id": str(geometry_id) if geometry_id else None,
                "geometry_wkt": geometry_wkt,
                "distance": distance
            },
            result_data=result_data,
            geometry=buffer_geometry,
            statistics=statistics,
            execution_time=execution_time
        )
        
        # 保存结果
        return await self.result_repository.create(result)
    
    async def distance_analysis(
        self,
        layer_id: UUID,
        geometry1_id: UUID,
        geometry2_id: UUID
    ) -> AnalysisResult:
        """距离分析"""
        start_time = time.time()
        
        # 获取两个几何要素
        feature1 = await self.feature_repository.get_by_id(geometry1_id)
        feature2 = await self.feature_repository.get_by_id(geometry2_id)
        
        if not feature1 or not feature2:
            raise ValueError("几何要素不存在")
        
        # 计算距离
        distance = feature1.geometry.distance(feature2.geometry)
        
        # 计算中心点
        centroid1 = feature1.geometry.centroid
        centroid2 = feature2.geometry.centroid
        
        result_data = {
            "distance": distance,
            "centroid1": centroid1.wkt,
            "centroid2": centroid2.wkt,
            "geometry1_id": str(geometry1_id),
            "geometry2_id": str(geometry2_id)
        }
        
        statistics = {
            "distance": distance,
            "centroid1_x": centroid1.x,
            "centroid1_y": centroid1.y,
            "centroid2_x": centroid2.x,
            "centroid2_y": centroid2.y
        }
        
        execution_time = time.time() - start_time
        
        result = AnalysisResult.create_new(
            analysis_type=AnalysisType.DISTANCE,
            input_parameters={
                "layer_id": str(layer_id),
                "geometry1_id": str(geometry1_id),
                "geometry2_id": str(geometry2_id)
            },
            result_data=result_data,
            statistics=statistics,
            execution_time=execution_time
        )
        
        return await self.result_repository.create(result)
    
    async def intersection_analysis(
        self,
        layer_id: UUID,
        geometry1_id: UUID,
        geometry2_id: UUID
    ) -> AnalysisResult:
        """相交分析"""
        start_time = time.time()
        
        # 获取两个几何要素
        feature1 = await self.feature_repository.get_by_id(geometry1_id)
        feature2 = await self.feature_repository.get_by_id(geometry2_id)
        
        if not feature1 or not feature2:
            raise ValueError("几何要素不存在")
        
        # 计算相交
        intersection = feature1.geometry.intersection(feature2.geometry)
        
        result_data = {
            "intersection_geometry": intersection.wkt if not intersection.is_empty else None,
            "intersection_area": intersection.area if not intersection.is_empty else 0,
            "geometry1_id": str(geometry1_id),
            "geometry2_id": str(geometry2_id)
        }
        
        statistics = {
            "intersection_area": intersection.area if not intersection.is_empty else 0,
            "has_intersection": not intersection.is_empty
        }
        
        execution_time = time.time() - start_time
        
        result = AnalysisResult.create_new(
            analysis_type=AnalysisType.INTERSECT,
            input_parameters={
                "layer_id": str(layer_id),
                "geometry1_id": str(geometry1_id),
                "geometry2_id": str(geometry2_id)
            },
            result_data=result_data,
            geometry=intersection if not intersection.is_empty else None,
            statistics=statistics,
            execution_time=execution_time
        )
        
        return await self.result_repository.create(result)
    
    async def union_analysis(
        self,
        layer_id: UUID,
        geometry_ids: List[UUID]
    ) -> AnalysisResult:
        """合并分析"""
        start_time = time.time()
        
        # 获取所有几何要素
        features = []
        for geom_id in geometry_ids:
            feature = await self.feature_repository.get_by_id(geom_id)
            if not feature:
                raise ValueError(f"几何要素不存在: {geom_id}")
            features.append(feature)
        
        # 执行合并
        geometries = [f.geometry for f in features]
        union_geometry = unary_union(geometries)
        
        result_data = {
            "union_geometry": union_geometry.wkt,
            "union_area": union_geometry.area,
            "geometry_ids": [str(gid) for gid in geometry_ids]
        }
        
        statistics = {
            "union_area": union_geometry.area,
            "input_count": len(geometry_ids)
        }
        
        execution_time = time.time() - start_time
        
        result = AnalysisResult.create_new(
            analysis_type=AnalysisType.UNION,
            input_parameters={
                "layer_id": str(layer_id),
                "geometry_ids": [str(gid) for gid in geometry_ids]
            },
            result_data=result_data,
            geometry=union_geometry,
            statistics=statistics,
            execution_time=execution_time
        )
        
        return await self.result_repository.create(result)
    
    async def accessibility_analysis(
        self,
        layer_id: UUID,
        center_geometry_id: UUID,
        max_distance: float
    ) -> AnalysisResult:
        """可达性分析"""
        start_time = time.time()
        
        # 获取中心几何
        center_feature = await self.feature_repository.get_by_id(center_geometry_id)
        if not center_feature:
            raise ValueError("中心几何要素不存在")
        
        # 获取图层所有要素
        all_features = await self.feature_repository.get_by_layer_id(layer_id)
        
        # 计算可达性
        accessible_features = []
        total_features = len(all_features)
        
        for feature in all_features:
            distance = center_feature.geometry.distance(feature.geometry)
            if distance <= max_distance:
                accessible_features.append({
                    "feature_id": str(feature.id),
                    "distance": distance,
                    "properties": feature.properties
                })
        
        accessibility_rate = len(accessible_features) / total_features if total_features > 0 else 0
        
        result_data = {
            "center_geometry_id": str(center_geometry_id),
            "max_distance": max_distance,
            "accessible_features": accessible_features,
            "total_features": total_features,
            "accessibility_rate": accessibility_rate
        }
        
        statistics = {
            "accessible_count": len(accessible_features),
            "total_count": total_features,
            "accessibility_rate": accessibility_rate,
            "max_distance": max_distance
        }
        
        execution_time = time.time() - start_time
        
        result = AnalysisResult.create_new(
            analysis_type=AnalysisType.ACCESSIBILITY,
            input_parameters={
                "layer_id": str(layer_id),
                "center_geometry_id": str(center_geometry_id),
                "max_distance": max_distance
            },
            result_data=result_data,
            statistics=statistics,
            execution_time=execution_time
        )
        
        return await self.result_repository.create(result)


class SpatialQueryService:
    """空间查询服务"""
    
    def __init__(
        self,
        layer_repository: LayerRepository,
        feature_repository: SpatialFeatureRepository,
        query_repository: SpatialQueryRepository
    ):
        self.layer_repository = layer_repository
        self.feature_repository = feature_repository
        self.query_repository = query_repository
    
    async def query_features_by_extent(
        self,
        layer_id: UUID,
        extent: SpatialExtent
    ) -> List[SpatialFeature]:
        """根据空间范围查询要素"""
        return await self.feature_repository.get_by_extent(layer_id, extent)
    
    async def query_features_by_geometry_type(
        self,
        layer_id: UUID,
        geometry_type: GeometryType
    ) -> List[SpatialFeature]:
        """根据几何类型查询要素"""
        return await self.feature_repository.get_by_geometry_type(layer_id, geometry_type)
    
    async def query_features_within_distance(
        self,
        layer_id: UUID,
        geometry: BaseGeometry,
        distance: float
    ) -> List[SpatialFeature]:
        """查询指定距离内的要素"""
        return await self.query_repository.find_features_within_distance(
            layer_id, geometry, distance
        )
    
    async def query_features_intersecting(
        self,
        layer_id: UUID,
        geometry: BaseGeometry
    ) -> List[SpatialFeature]:
        """查询相交的要素"""
        return await self.query_repository.find_features_intersecting(layer_id, geometry)
    
    async def query_features_containing(
        self,
        layer_id: UUID,
        geometry: BaseGeometry
    ) -> List[SpatialFeature]:
        """查询包含指定几何的要素"""
        return await self.query_repository.find_features_containing(layer_id, geometry)
    
    async def query_features_within(
        self,
        layer_id: UUID,
        geometry: BaseGeometry
    ) -> List[SpatialFeature]:
        """查询在指定几何内的要素"""
        return await self.query_repository.find_features_within(layer_id, geometry)
    
    async def execute_complex_query(
        self,
        query: SpatialQuery
    ) -> List[SpatialFeature]:
        """执行复杂查询"""
        if query.query_type == QueryType.SPATIAL:
            return await self.query_repository.execute_spatial_query(query)
        elif query.query_type == QueryType.ATTRIBUTE:
            return await self.query_repository.execute_attribute_query(query)
        elif query.query_type == QueryType.HYBRID:
            return await self.query_repository.execute_hybrid_query(query)
        elif query.query_type == QueryType.SQL:
            # SQL查询返回字典格式
            results = await self.query_repository.execute_sql_query(query)
            # 这里需要将字典结果转换为SpatialFeature对象
            # 具体实现取决于数据库结构
            return []
        else:
            raise ValueError(f"不支持的查询类型: {query.query_type}")


class LayerManagementService:
    """图层管理服务"""
    
    def __init__(
        self,
        layer_repository: LayerRepository,
        feature_repository: SpatialFeatureRepository
    ):
        self.layer_repository = layer_repository
        self.feature_repository = feature_repository
    
    async def create_layer(
        self,
        name: str,
        description: str,
        geometry_type: GeometryType,
        srid: int = 4326
    ) -> Layer:
        """创建图层"""
        layer = Layer.create_new(name, description, geometry_type, srid)
        return await self.layer_repository.create(layer)
    
    async def update_layer_metadata(
        self,
        layer_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_visible: Optional[bool] = None,
        opacity: Optional[float] = None,
        style: Optional[Dict[str, Any]] = None
    ) -> Layer:
        """更新图层元数据"""
        layer = await self.layer_repository.get_by_id(layer_id)
        if not layer:
            raise ValueError(f"图层不存在: {layer_id}")
        
        if name is not None:
            layer.name = name
        if description is not None:
            layer.description = description
        if is_visible is not None:
            layer.is_visible = is_visible
        if opacity is not None:
            layer.opacity = opacity
        if style is not None:
            layer.style = style
        
        layer.updated_at = datetime.utcnow()
        return await self.layer_repository.update(layer)
    
    async def calculate_layer_statistics(self, layer_id: UUID) -> Dict[str, Any]:
        """计算图层统计信息"""
        # 获取要素数量
        feature_count = await self.feature_repository.count_by_layer_id(layer_id)
        
        # 获取空间范围
        extent = await self.feature_repository.get_extent_by_layer_id(layer_id)
        
        # 更新图层信息
        if extent:
            await self.layer_repository.update_extent(layer_id, extent)
        await self.layer_repository.update_feature_count(layer_id, feature_count)
        
        return {
            "feature_count": feature_count,
            "extent": extent.to_dict() if extent else None
        }
    
    async def delete_layer(self, layer_id: UUID) -> bool:
        """删除图层"""
        # 先删除所有要素
        await self.feature_repository.delete_by_layer_id(layer_id)
        # 再删除图层
        return await self.layer_repository.delete(layer_id)
