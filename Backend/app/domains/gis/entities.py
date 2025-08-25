"""
GIS领域 - 实体定义
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4
from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon
from shapely.geometry.base import BaseGeometry
import json


class GeometryType(Enum):
    """几何类型"""
    POINT = "Point"
    LINESTRING = "LineString"
    POLYGON = "Polygon"
    MULTIPOINT = "MultiPoint"
    MULTILINESTRING = "MultiLineString"
    MULTIPOLYGON = "MultiPolygon"


class AnalysisType(Enum):
    """分析类型"""
    BUFFER = "buffer"
    DISTANCE = "distance"
    INTERSECT = "intersect"
    UNION = "union"
    DIFFERENCE = "difference"
    ACCESSIBILITY = "accessibility"
    OVERLAY = "overlay"
    STATISTICAL = "statistical"


class QueryType(Enum):
    """查询类型"""
    SPATIAL = "spatial"
    ATTRIBUTE = "attribute"
    HYBRID = "hybrid"
    SQL = "sql"


@dataclass
class SpatialExtent:
    """空间范围"""
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    srid: int = 4326  # 默认WGS84
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_x": self.min_x,
            "min_y": self.min_y,
            "max_x": self.max_x,
            "max_y": self.max_y,
            "srid": self.srid
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpatialExtent":
        return cls(
            min_x=data["min_x"],
            min_y=data["min_y"],
            max_x=data["max_x"],
            max_y=data["max_y"],
            srid=data.get("srid", 4326)
        )


@dataclass
class SpatialFeature:
    """空间要素"""
    id: UUID
    geometry: BaseGeometry
    properties: Dict[str, Any]
    layer_id: UUID
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    @classmethod
    def create_new(
        cls,
        geometry: BaseGeometry,
        properties: Dict[str, Any],
        layer_id: UUID
    ) -> "SpatialFeature":
        return cls(
            id=uuid4(),
            geometry=geometry,
            properties=properties,
            layer_id=layer_id
        )
    
    def get_geometry_type(self) -> GeometryType:
        """获取几何类型"""
        if isinstance(self.geometry, Point):
            return GeometryType.POINT
        elif isinstance(self.geometry, LineString):
            return GeometryType.LINESTRING
        elif isinstance(self.geometry, Polygon):
            return GeometryType.POLYGON
        elif isinstance(self.geometry, MultiPoint):
            return GeometryType.MULTIPOINT
        elif isinstance(self.geometry, MultiLineString):
            return GeometryType.MULTILINESTRING
        elif isinstance(self.geometry, MultiPolygon):
            return GeometryType.MULTIPOLYGON
        else:
            raise ValueError(f"Unsupported geometry type: {type(self.geometry)}")
    
    def to_geojson(self) -> Dict[str, Any]:
        """转换为GeoJSON格式"""
        return {
            "type": "Feature",
            "geometry": {
                "type": self.get_geometry_type().value,
                "coordinates": self.geometry.__geo_interface__["coordinates"]
            },
            "properties": {
                "id": str(self.id),
                "layer_id": str(self.layer_id),
                **self.properties
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": str(self.id),
            "geometry_type": self.get_geometry_type().value,
            "geometry": self.geometry.wkt,
            "properties": self.properties,
            "layer_id": str(self.layer_id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Layer:
    """图层"""
    id: UUID
    name: str
    description: str
    geometry_type: GeometryType
    srid: int
    extent: Optional[SpatialExtent] = None
    feature_count: int = 0
    is_visible: bool = True
    opacity: float = 1.0
    style: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    @classmethod
    def create_new(
        cls,
        name: str,
        description: str,
        geometry_type: GeometryType,
        srid: int = 4326
    ) -> "Layer":
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            geometry_type=geometry_type,
            srid=srid
        )
    
    def update_extent(self, extent: SpatialExtent) -> None:
        """更新空间范围"""
        self.extent = extent
        self.updated_at = datetime.utcnow()
    
    def update_feature_count(self, count: int) -> None:
        """更新要素数量"""
        self.feature_count = count
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "geometry_type": self.geometry_type.value,
            "srid": self.srid,
            "extent": self.extent.to_dict() if self.extent else None,
            "feature_count": self.feature_count,
            "is_visible": self.is_visible,
            "opacity": self.opacity,
            "style": self.style,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class AnalysisResult:
    """分析结果"""
    id: UUID
    analysis_type: AnalysisType
    input_parameters: Dict[str, Any]
    result_data: Dict[str, Any]
    geometry: Optional[BaseGeometry] = None
    statistics: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create_new(
        cls,
        analysis_type: AnalysisType,
        input_parameters: Dict[str, Any],
        result_data: Dict[str, Any],
        geometry: Optional[BaseGeometry] = None,
        statistics: Optional[Dict[str, Any]] = None,
        execution_time: float = 0.0
    ) -> "AnalysisResult":
        return cls(
            id=uuid4(),
            analysis_type=analysis_type,
            input_parameters=input_parameters,
            result_data=result_data,
            geometry=geometry,
            statistics=statistics or {},
            execution_time=execution_time
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": str(self.id),
            "analysis_type": self.analysis_type.value,
            "input_parameters": self.input_parameters,
            "result_data": self.result_data,
            "geometry": self.geometry.wkt if self.geometry else None,
            "statistics": self.statistics,
            "execution_time": self.execution_time,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class SpatialQuery:
    """空间查询"""
    id: UUID
    query_type: QueryType
    query_parameters: Dict[str, Any]
    spatial_filter: Optional[Dict[str, Any]] = None
    attribute_filter: Optional[Dict[str, Any]] = None
    sql_query: Optional[str] = None
    limit: int = 1000
    offset: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create_spatial_query(
        cls,
        spatial_filter: Dict[str, Any],
        limit: int = 1000,
        offset: int = 0
    ) -> "SpatialQuery":
        return cls(
            id=uuid4(),
            query_type=QueryType.SPATIAL,
            query_parameters={},
            spatial_filter=spatial_filter,
            limit=limit,
            offset=offset
        )
    
    @classmethod
    def create_attribute_query(
        cls,
        attribute_filter: Dict[str, Any],
        limit: int = 1000,
        offset: int = 0
    ) -> "SpatialQuery":
        return cls(
            id=uuid4(),
            query_type=QueryType.ATTRIBUTE,
            query_parameters={},
            attribute_filter=attribute_filter,
            limit=limit,
            offset=offset
        )
    
    @classmethod
    def create_sql_query(
        cls,
        sql_query: str,
        limit: int = 1000,
        offset: int = 0
    ) -> "SpatialQuery":
        return cls(
            id=uuid4(),
            query_type=QueryType.SQL,
            query_parameters={},
            sql_query=sql_query,
            limit=limit,
            offset=offset
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": str(self.id),
            "query_type": self.query_type.value,
            "query_parameters": self.query_parameters,
            "spatial_filter": self.spatial_filter,
            "attribute_filter": self.attribute_filter,
            "sql_query": self.sql_query,
            "limit": self.limit,
            "offset": self.offset,
            "created_at": self.created_at.isoformat()
        }

