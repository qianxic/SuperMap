"""
GIS数据传输对象
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


# 图层相关DTO
class LayerCreateDTO(BaseModel):
    """创建图层DTO"""
    name: str = Field(..., description="图层名称", min_length=1, max_length=100)
    description: str = Field(..., description="图层描述", max_length=500)
    geometry_type: str = Field(..., description="几何类型")
    srid: int = Field(default=4326, description="空间参考系统ID")


class LayerUpdateDTO(BaseModel):
    """更新图层DTO"""
    name: Optional[str] = Field(None, description="图层名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="图层描述", max_length=500)
    is_visible: Optional[bool] = Field(None, description="是否可见")
    opacity: Optional[float] = Field(None, ge=0.0, le=1.0, description="透明度")
    style: Optional[Dict[str, Any]] = Field(None, description="样式配置")


class LayerResponseDTO(BaseModel):
    """图层响应DTO"""
    id: str
    name: str
    description: str
    geometry_type: str
    srid: int
    extent: Optional[Dict[str, Any]] = None
    feature_count: int
    is_visible: bool
    opacity: float
    style: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


# 空间要素相关DTO
class SpatialFeatureCreateDTO(BaseModel):
    """创建空间要素DTO"""
    geometry_wkt: str = Field(..., description="几何WKT格式")
    properties: Dict[str, Any] = Field(default_factory=dict, description="属性数据")
    layer_id: str = Field(..., description="所属图层ID")


class SpatialFeatureUpdateDTO(BaseModel):
    """更新空间要素DTO"""
    geometry_wkt: Optional[str] = Field(None, description="几何WKT格式")
    properties: Optional[Dict[str, Any]] = Field(None, description="属性数据")


class SpatialFeatureResponseDTO(BaseModel):
    """空间要素响应DTO"""
    id: str
    geometry_type: str
    geometry: str  # WKT格式
    properties: Dict[str, Any]
    layer_id: str
    created_at: datetime
    updated_at: datetime


class GeoJSONFeatureDTO(BaseModel):
    """GeoJSON要素DTO"""
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


# 空间分析相关DTO
class BufferAnalysisDTO(BaseModel):
    """缓冲区分析DTO"""
    layer_id: str = Field(..., description="图层ID")
    distance: float = Field(..., gt=0, description="缓冲区距离")
    geometry_id: Optional[str] = Field(None, description="几何要素ID")
    geometry_wkt: Optional[str] = Field(None, description="几何WKT格式")


class DistanceAnalysisDTO(BaseModel):
    """距离分析DTO"""
    layer_id: str = Field(..., description="图层ID")
    geometry1_id: str = Field(..., description="第一个几何要素ID")
    geometry2_id: str = Field(..., description="第二个几何要素ID")


class IntersectionAnalysisDTO(BaseModel):
    """相交分析DTO"""
    layer_id: str = Field(..., description="图层ID")
    geometry1_id: str = Field(..., description="第一个几何要素ID")
    geometry2_id: str = Field(..., description="第二个几何要素ID")


class UnionAnalysisDTO(BaseModel):
    """合并分析DTO"""
    layer_id: str = Field(..., description="图层ID")
    geometry_ids: List[str] = Field(..., min_items=2, description="几何要素ID列表")


class AccessibilityAnalysisDTO(BaseModel):
    """可达性分析DTO"""
    layer_id: str = Field(..., description="图层ID")
    center_geometry_id: str = Field(..., description="中心几何要素ID")
    max_distance: float = Field(..., gt=0, description="最大距离")


class AnalysisResultDTO(BaseModel):
    """分析结果DTO"""
    id: str
    analysis_type: str
    input_parameters: Dict[str, Any]
    result_data: Dict[str, Any]
    geometry: Optional[str] = None  # WKT格式
    statistics: Dict[str, Any]
    execution_time: float
    created_at: datetime


# 空间查询相关DTO
class ExtentQueryDTO(BaseModel):
    """空间范围查询DTO"""
    layer_id: str = Field(..., description="图层ID")
    extent: Dict[str, Any] = Field(..., description="空间范围")


class GeometryTypeQueryDTO(BaseModel):
    """几何类型查询DTO"""
    layer_id: str = Field(..., description="图层ID")
    geometry_type: str = Field(..., description="几何类型")


class DistanceQueryDTO(BaseModel):
    """距离查询DTO"""
    layer_id: str = Field(..., description="图层ID")
    geometry_wkt: str = Field(..., description="查询几何WKT格式")
    distance: float = Field(..., gt=0, description="查询距离")


class SpatialQueryDTO(BaseModel):
    """空间查询DTO"""
    layer_id: str = Field(..., description="图层ID")
    geometry_wkt: str = Field(..., description="查询几何WKT格式")


class ComplexQueryDTO(BaseModel):
    """复杂查询DTO"""
    layer_id: str = Field(..., description="图层ID")
    spatial_filter: Optional[Dict[str, Any]] = Field(None, description="空间过滤条件")
    attribute_filter: Optional[Dict[str, Any]] = Field(None, description="属性过滤条件")
    sql_query: Optional[str] = Field(None, description="SQL查询语句")
    limit: int = Field(default=1000, ge=1, le=10000, description="返回记录数限制")
    offset: int = Field(default=0, ge=0, description="跳过记录数")


class QueryResultDTO(BaseModel):
    """查询结果DTO"""
    layer_id: str
    features: List[GeoJSONFeatureDTO]
    total_count: int
    limit: int
    offset: int


# 空间范围DTO
class SpatialExtentDTO(BaseModel):
    """空间范围DTO"""
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    srid: int = 4326


# 统计信息DTO
class LayerStatisticsDTO(BaseModel):
    """图层统计信息DTO"""
    feature_count: int
    extent: Optional[SpatialExtentDTO] = None
    geometry_types: Dict[str, int] = Field(default_factory=dict)
    attribute_fields: List[str] = Field(default_factory=list)


# 批量操作DTO
class BatchFeatureCreateDTO(BaseModel):
    """批量创建要素DTO"""
    layer_id: str = Field(..., description="图层ID")
    features: List[SpatialFeatureCreateDTO] = Field(..., min_items=1, description="要素列表")


class BatchFeatureUpdateDTO(BaseModel):
    """批量更新要素DTO"""
    layer_id: str = Field(..., description="图层ID")
    features: List[Dict[str, Any]] = Field(..., min_items=1, description="要素更新数据")


class BatchOperationResultDTO(BaseModel):
    """批量操作结果DTO"""
    success_count: int
    failed_count: int
    errors: List[str] = Field(default_factory=list)
    operation_type: str


# 导入导出DTO
class DataImportDTO(BaseModel):
    """数据导入DTO"""
    layer_id: str = Field(..., description="图层ID")
    file_format: str = Field(..., description="文件格式", regex="^(geojson|shapefile|csv)$")
    file_content: str = Field(..., description="文件内容或路径")
    encoding: str = Field(default="utf-8", description="文件编码")


class DataExportDTO(BaseModel):
    """数据导出DTO"""
    layer_id: str = Field(..., description="图层ID")
    format: str = Field(..., description="导出格式", regex="^(geojson|shapefile|csv)$")
    extent: Optional[SpatialExtentDTO] = Field(None, description="导出范围")
    attributes: Optional[List[str]] = Field(None, description="导出属性字段")


# 响应包装DTO
class GISResponseDTO(BaseModel):
    """GIS响应包装DTO"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[int] = None


class PaginatedResponseDTO(BaseModel):
    """分页响应DTO"""
    success: bool
    message: str
    data: Dict[str, Any]
    pagination: Dict[str, Any]