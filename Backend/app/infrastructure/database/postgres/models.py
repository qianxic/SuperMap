"""
PostgreSQL数据库模型
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, GEOMETRY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class UserModel(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class LayerModel(Base):
    """图层模型"""
    __tablename__ = "layers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    geometry_type = Column(String(50), nullable=False)  # Point, LineString, Polygon等
    srid = Column(Integer, default=4326, nullable=False)
    extent_min_x = Column(Float, nullable=True)
    extent_min_y = Column(Float, nullable=True)
    extent_max_x = Column(Float, nullable=True)
    extent_max_y = Column(Float, nullable=True)
    feature_count = Column(Integer, default=0)
    is_visible = Column(Boolean, default=True)
    opacity = Column(Float, default=1.0)
    style = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    features = relationship("SpatialFeatureModel", back_populates="layer", cascade="all, delete-orphan")


class SpatialFeatureModel(Base):
    """空间要素模型"""
    __tablename__ = "spatial_features"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    layer_id = Column(UUID(as_uuid=True), ForeignKey("layers.id"), nullable=False, index=True)
    geometry = Column(GEOMETRY(geometry_type='GEOMETRY', srid=4326), nullable=False)
    properties = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    layer = relationship("LayerModel", back_populates="features")


class AnalysisResultModel(Base):
    """分析结果模型"""
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_type = Column(String(50), nullable=False, index=True)  # buffer, distance, intersect等
    input_parameters = Column(JSON, nullable=False)
    result_data = Column(JSON, nullable=False)
    geometry = Column(GEOMETRY(geometry_type='GEOMETRY', srid=4326), nullable=True)
    statistics = Column(JSON, default={})
    execution_time = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
