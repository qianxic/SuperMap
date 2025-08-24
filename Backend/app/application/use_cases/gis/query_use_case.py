"""
GIS查询用例
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry

from app.domains.gis.services import SpatialQueryService
from app.domains.gis.entities import QueryType, GeometryType, SpatialExtent
from app.domains.gis.repositories import (
    LayerRepository, SpatialFeatureRepository, SpatialQueryRepository
)


class GISQueryUseCase:
    """GIS查询用例"""
    
    def __init__(
        self,
        layer_repository: LayerRepository,
        feature_repository: SpatialFeatureRepository,
        query_repository: SpatialQueryRepository
    ):
        self.query_service = SpatialQueryService(
            layer_repository, feature_repository, query_repository
        )
        self.layer_repository = layer_repository
        self.feature_repository = feature_repository
        self.query_repository = query_repository
    
    async def query_features_by_extent(
        self,
        layer_id: str,
        extent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """根据空间范围查询要素"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 创建空间范围对象
            spatial_extent = SpatialExtent.from_dict(extent)
            
            # 执行查询
            features = await self.query_service.query_features_by_extent(
                UUID(layer_id), spatial_extent
            )
            
            return {
                "success": True,
                "message": "空间范围查询完成",
                "data": {
                    "layer_id": layer_id,
                    "extent": extent,
                    "features": [feature.to_geojson() for feature in features],
                    "total_count": len(features)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"空间范围查询失败: {str(e)}",
                "data": None
            }
    
    async def query_features_by_geometry_type(
        self,
        layer_id: str,
        geometry_type: str
    ) -> Dict[str, Any]:
        """根据几何类型查询要素"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 验证几何类型
            try:
                geom_type_enum = GeometryType(geometry_type)
            except ValueError:
                raise ValueError(f"不支持的几何类型: {geometry_type}")
            
            # 执行查询
            features = await self.query_service.query_features_by_geometry_type(
                UUID(layer_id), geom_type_enum
            )
            
            return {
                "success": True,
                "message": "几何类型查询完成",
                "data": {
                    "layer_id": layer_id,
                    "geometry_type": geometry_type,
                    "features": [feature.to_geojson() for feature in features],
                    "total_count": len(features)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"几何类型查询失败: {str(e)}",
                "data": None
            }
    
    async def query_features_within_distance(
        self,
        layer_id: str,
        geometry_wkt: str,
        distance: float
    ) -> Dict[str, Any]:
        """查询指定距离内的要素"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 解析几何
            geometry = shape(geometry_wkt)
            
            # 执行查询
            features = await self.query_service.query_features_within_distance(
                UUID(layer_id), geometry, distance
            )
            
            return {
                "success": True,
                "message": "距离查询完成",
                "data": {
                    "layer_id": layer_id,
                    "geometry": geometry_wkt,
                    "distance": distance,
                    "features": [feature.to_geojson() for feature in features],
                    "total_count": len(features)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"距离查询失败: {str(e)}",
                "data": None
            }
    
    async def query_features_intersecting(
        self,
        layer_id: str,
        geometry_wkt: str
    ) -> Dict[str, Any]:
        """查询相交的要素"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 解析几何
            geometry = shape(geometry_wkt)
            
            # 执行查询
            features = await self.query_service.query_features_intersecting(
                UUID(layer_id), geometry
            )
            
            return {
                "success": True,
                "message": "相交查询完成",
                "data": {
                    "layer_id": layer_id,
                    "geometry": geometry_wkt,
                    "features": [feature.to_geojson() for feature in features],
                    "total_count": len(features)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"相交查询失败: {str(e)}",
                "data": None
            }
    
    async def query_features_containing(
        self,
        layer_id: str,
        geometry_wkt: str
    ) -> Dict[str, Any]:
        """查询包含指定几何的要素"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 解析几何
            geometry = shape(geometry_wkt)
            
            # 执行查询
            features = await self.query_service.query_features_containing(
                UUID(layer_id), geometry
            )
            
            return {
                "success": True,
                "message": "包含查询完成",
                "data": {
                    "layer_id": layer_id,
                    "geometry": geometry_wkt,
                    "features": [feature.to_geojson() for feature in features],
                    "total_count": len(features)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"包含查询失败: {str(e)}",
                "data": None
            }
    
    async def query_features_within(
        self,
        layer_id: str,
        geometry_wkt: str
    ) -> Dict[str, Any]:
        """查询在指定几何内的要素"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 解析几何
            geometry = shape(geometry_wkt)
            
            # 执行查询
            features = await self.query_service.query_features_within(
                UUID(layer_id), geometry
            )
            
            return {
                "success": True,
                "message": "内部查询完成",
                "data": {
                    "layer_id": layer_id,
                    "geometry": geometry_wkt,
                    "features": [feature.to_geojson() for feature in features],
                    "total_count": len(features)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"内部查询失败: {str(e)}",
                "data": None
            }
    
    async def execute_spatial_query(
        self,
        layer_id: str,
        spatial_filter: Dict[str, Any],
        limit: int = 1000,
        offset: int = 0
    ) -> Dict[str, Any]:
        """执行空间查询"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 创建查询对象
            query = self.query_repository.create_spatial_query(
                spatial_filter, limit, offset
            )
            
            # 执行查询
            features = await self.query_service.execute_complex_query(query)
            
            return {
                "success": True,
                "message": "空间查询完成",
                "data": {
                    "layer_id": layer_id,
                    "spatial_filter": spatial_filter,
                    "features": [feature.to_geojson() for feature in features],
                    "total_count": len(features),
                    "limit": limit,
                    "offset": offset
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"空间查询失败: {str(e)}",
                "data": None
            }
    
    async def execute_attribute_query(
        self,
        layer_id: str,
        attribute_filter: Dict[str, Any],
        limit: int = 1000,
        offset: int = 0
    ) -> Dict[str, Any]:
        """执行属性查询"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 创建查询对象
            query = self.query_repository.create_attribute_query(
                attribute_filter, limit, offset
            )
            
            # 执行查询
            features = await self.query_service.execute_complex_query(query)
            
            return {
                "success": True,
                "message": "属性查询完成",
                "data": {
                    "layer_id": layer_id,
                    "attribute_filter": attribute_filter,
                    "features": [feature.to_geojson() for feature in features],
                    "total_count": len(features),
                    "limit": limit,
                    "offset": offset
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"属性查询失败: {str(e)}",
                "data": None
            }
    
    async def execute_sql_query(
        self,
        layer_id: str,
        sql_query: str,
        limit: int = 1000,
        offset: int = 0
    ) -> Dict[str, Any]:
        """执行SQL查询"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 创建查询对象
            query = self.query_repository.create_sql_query(sql_query, limit, offset)
            
            # 执行查询
            results = await self.query_repository.execute_sql_query(query)
            
            return {
                "success": True,
                "message": "SQL查询完成",
                "data": {
                    "layer_id": layer_id,
                    "sql_query": sql_query,
                    "results": results,
                    "total_count": len(results),
                    "limit": limit,
                    "offset": offset
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"SQL查询失败: {str(e)}",
                "data": None
            }
    
    async def get_layer_features(
        self,
        layer_id: str,
        skip: int = 0,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """获取图层所有要素"""
        try:
            # 验证图层存在
            layer = await self.layer_repository.get_by_id(UUID(layer_id))
            if not layer:
                raise ValueError(f"图层不存在: {layer_id}")
            
            # 获取要素
            features = await self.feature_repository.get_by_layer_id(
                UUID(layer_id), skip, limit
            )
            
            return {
                "success": True,
                "message": "获取图层要素完成",
                "data": {
                    "layer_id": layer_id,
                    "layer_info": layer.to_dict(),
                    "features": [feature.to_geojson() for feature in features],
                    "total_count": len(features),
                    "skip": skip,
                    "limit": limit
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"获取图层要素失败: {str(e)}",
                "data": None
            }