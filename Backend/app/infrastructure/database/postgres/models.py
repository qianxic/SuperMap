"""
PostgreSQL数据库模型模块
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class UserModel(Base):
    """用户数据库模型"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at is not None else None,
            "last_login": self.last_login.isoformat() if self.last_login is not None else None
        }


class LayerModel(Base):
    """图层数据库模型
    
    注意: 此模型定义需要根据您实际制作的表结构进行调整
    当前为参考定义，请根据实际表结构修改字段名称和类型
    """
    __tablename__ = "layers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    geometry_type = Column(String(50), nullable=False)  # Point, LineString, Polygon, etc.
    srid = Column(Integer, default=4326, nullable=False)
    extent = Column(JSONB, nullable=True)  # 空间范围
    feature_count = Column(Integer, default=0, nullable=False)
    is_visible = Column(Boolean, default=True, nullable=False)
    opacity = Column(Float, default=1.0, nullable=False)
    style = Column(JSONB, nullable=True)  # 样式配置
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    created_by_user = relationship("UserModel", foreign_keys=[created_by])
    features = relationship("SpatialFeatureModel", back_populates="layer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LayerModel(id={self.id}, name='{self.name}', geometry_type='{self.geometry_type}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "geometry_type": self.geometry_type,
            "srid": self.srid,
            "extent": self.extent,
            "feature_count": self.feature_count,
            "is_visible": self.is_visible,
            "opacity": self.opacity,
            "style": self.style,
            "created_by": str(self.created_by) if self.created_by is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at is not None else None
        }


class SpatialFeatureModel(Base):
    """空间要素数据库模型
    
    注意: 此模型定义需要根据您实际制作的表结构进行调整
    当前为参考定义，请根据实际表结构修改字段名称和类型
    """
    __tablename__ = "spatial_features"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    layer_id = Column(UUID(as_uuid=True), ForeignKey("layers.id"), nullable=False, index=True)
    geometry_wkt = Column(Text, nullable=False)  # WKT格式的几何数据
    properties = Column(JSONB, nullable=True)  # 属性数据
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    layer = relationship("LayerModel", back_populates="features")
    
    def __repr__(self):
        return f"<SpatialFeatureModel(id={self.id}, layer_id={self.layer_id})>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": str(self.id),
            "layer_id": str(self.layer_id),
            "geometry_wkt": self.geometry_wkt,
            "properties": self.properties,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at is not None else None
        }


class AnalysisResultModel(Base):
    """分析结果数据库模型
    
    注意: 此模型定义需要根据您实际制作的表结构进行调整
    当前为参考定义，请根据实际表结构修改字段名称和类型
    """
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_type = Column(String(100), nullable=False, index=True)  # buffer, distance, etc.
    layer_id = Column(UUID(as_uuid=True), ForeignKey("layers.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    input_parameters = Column(JSONB, nullable=True)  # 输入参数
    result_data = Column(JSONB, nullable=True)  # 结果数据
    geometry_wkt = Column(Text, nullable=True)  # 结果几何数据
    statistics = Column(JSONB, nullable=True)  # 统计信息
    execution_time = Column(Float, default=0.0, nullable=False)  # 执行时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    layer = relationship("LayerModel")
    user = relationship("UserModel")
    
    def __repr__(self):
        return f"<AnalysisResultModel(id={self.id}, analysis_type='{self.analysis_type}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": str(self.id),
            "analysis_type": self.analysis_type,
            "layer_id": str(self.layer_id) if self.layer_id is not None else None,
            "user_id": str(self.user_id) if self.user_id is not None else None,
            "input_parameters": self.input_parameters,
            "result_data": self.result_data,
            "geometry_wkt": self.geometry_wkt,
            "statistics": self.statistics,
            "execution_time": self.execution_time,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None
        }


class SpatialQueryModel(Base):
    """空间查询数据库模型
    
    注意: 此模型定义需要根据您实际制作的表结构进行调整
    当前为参考定义，请根据实际表结构修改字段名称和类型
    """
    __tablename__ = "spatial_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_type = Column(String(50), nullable=False, index=True)  # spatial, attribute, sql, hybrid
    layer_id = Column(UUID(as_uuid=True), ForeignKey("layers.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    query_parameters = Column(JSONB, nullable=True)  # 查询参数
    spatial_filter = Column(JSONB, nullable=True)  # 空间过滤条件
    attribute_filter = Column(JSONB, nullable=True)  # 属性过滤条件
    sql_query = Column(Text, nullable=True)  # SQL查询语句
    limit = Column(Integer, default=1000, nullable=False)
    offset = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    layer = relationship("LayerModel")
    user = relationship("UserModel")
    
    def __repr__(self):
        return f"<SpatialQueryModel(id={self.id}, query_type='{self.query_type}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": str(self.id),
            "query_type": self.query_type,
            "layer_id": str(self.layer_id) if self.layer_id is not None else None,
            "user_id": str(self.user_id) if self.user_id is not None else None,
            "query_parameters": self.query_parameters,
            "spatial_filter": self.spatial_filter,
            "attribute_filter": self.attribute_filter,
            "sql_query": self.sql_query,
            "limit": self.limit,
            "offset": self.offset,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None
        }
