"""
GIS模块数据传输对象 (DTO)
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


# ==================== 空间分析 DTO ====================

class BufferAnalysisRequest(BaseModel):
    """缓冲区分析请求"""
    layer_id: str = Field(..., description="图层ID")
    distance: float = Field(..., gt=0, description="缓冲区距离")
    geometry_id: Optional[str] = Field(None, description="几何要素ID")
    geometry_wkt: Optional[str] = Field(None, description="几何要素WKT字符串")
    
    @validator('distance')
    def validate_distance(cls, v):
        if v <= 0:
            raise ValueError('缓冲区距离必须大于0')
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
    geometry_ids: List[str] = Field(..., min_length=2, description="要合并的几何要素ID列表")


class AccessibilityAnalysisRequest(BaseModel):
    """可达性分析请求"""
    layer_id: str = Field(..., description="图层ID")
    center_geometry_id: str = Field(..., description="中心几何要素ID")
    max_distance: float = Field(..., gt=0, description="最大可达距离")
    
    @validator('max_distance')
    def validate_max_distance(cls, v):
        if v <= 0:
            raise ValueError('最大可达距离必须大于0')
        return v


# ==================== 空间查询 DTO ====================

class ExtentQueryRequest(BaseModel):
    """空间范围查询请求"""
    layer_id: str = Field(..., description="图层ID")
    extent: Dict[str, Any] = Field(..., description="空间范围")


class GeometryTypeQueryRequest(BaseModel):
    """几何类型查询请求"""
    layer_id: str = Field(..., description="图层ID")
    geometry_type: str = Field(..., description="几何类型")


class DistanceQueryRequest(BaseModel):
    """距离查询请求"""
    layer_id: str = Field(..., description="图层ID")
    geometry_wkt: str = Field(..., description="查询几何要素WKT")
    distance: float = Field(..., gt=0, description="查询距离")
    
    @validator('distance')
    def validate_distance(cls, v):
        if v <= 0:
            raise ValueError('查询距离必须大于0')
        return v


class SpatialQueryRequest(BaseModel):
    """空间查询请求"""
    layer_id: str = Field(..., description="图层ID")
    geometry_wkt: str = Field(..., description="查询几何要素WKT")


class ComplexQueryRequest(BaseModel):
    """复杂查询请求"""
    layer_id: str = Field(..., description="图层ID")
    spatial_filter: Optional[Dict[str, Any]] = Field(None, description="空间过滤条件")
    attribute_filter: Optional[Dict[str, Any]] = Field(None, description="属性过滤条件")
    sql_query: Optional[str] = Field(None, description="SQL查询语句")
    limit: int = Field(1000, ge=1, le=10000, description="返回结果数量限制")
    offset: int = Field(0, ge=0, description="结果偏移量")
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 10000:
            raise ValueError('结果数量限制必须在1-10000之间')
        return v


# ==================== 通用响应 DTO ====================

class GeometryData(BaseModel):
    """几何数据"""
    id: str
    geometry_type: str
    coordinates: List[Any]
    properties: Dict[str, Any]


class AnalysisResult(BaseModel):
    """分析结果"""
    analysis_id: str
    analysis_type: str
    input_parameters: Dict[str, Any]
    result_geometries: List[GeometryData]
    statistics: Dict[str, Any]
    created_at: datetime


class QueryResult(BaseModel):
    """查询结果"""
    total_count: int
    returned_count: int
    features: List[GeometryData]
    extent: Optional[Dict[str, Any]] = None


class GISResponse(BaseModel):
    """GIS操作响应"""
    success: bool
    message: str
    data: Optional[Union[AnalysisResult, QueryResult, Dict[str, Any]]] = None
    error_code: Optional[str] = None


# ==================== 图层管理 DTO ====================

class LayerInfo(BaseModel):
    """图层信息"""
    layer_id: str
    layer_name: str
    layer_type: str
    geometry_type: str
    feature_count: int
    extent: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class LayerListResponse(BaseModel):
    """图层列表响应"""
    success: bool
    message: str
    data: List[LayerInfo]
    total_count: int
