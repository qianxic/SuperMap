"""
PostgreSQL仓储实现
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func, text
from sqlalchemy.orm import selectinload
from datetime import datetime
from shapely.geometry import shape, Point, LineString, Polygon
from shapely.wkt import loads

from .models import UserModel, LayerModel, SpatialFeatureModel, AnalysisResultModel
from app.domains.user.repositories import UserRepository
from app.domains.user.entities import UserEntity
from app.domains.gis.repositories import (
    LayerRepository, SpatialFeatureRepository, AnalysisResultRepository, SpatialQueryRepository
)
from app.domains.gis.entities import (
    Layer, SpatialFeature, AnalysisResult, SpatialQuery,
    SpatialExtent, GeometryType, AnalysisType, QueryType
)
from shapely.geometry.base import BaseGeometry


class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL用户仓储实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: UserEntity) -> UserEntity:
        """创建用户"""
        user_model = UserModel(
            username=user.username,
            email=user.email,
            phone=user.phone,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_superuser=user.is_superuser
        )
        
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)
        
        return self._model_to_entity(user_model)
    
    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        """根据ID获取用户"""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return self._model_to_entity(user_model)
        return None
    
    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        """根据用户名获取用户"""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return self._model_to_entity(user_model)
        return None
    
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """根据邮箱获取用户"""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return self._model_to_entity(user_model)
        return None
    
    async def get_by_phone(self, phone: str) -> Optional[UserEntity]:
        """根据手机号获取用户"""
        stmt = select(UserModel).where(UserModel.phone == phone)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return self._model_to_entity(user_model)
        return None
    
    async def get_by_login_identifier(self, identifier: str) -> Optional[UserEntity]:
        """根据登录标识符（用户名/邮箱/手机号）获取用户"""
        stmt = select(UserModel).where(
            or_(
                UserModel.username == identifier,
                UserModel.email == identifier,
                UserModel.phone == identifier
            )
        )
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return self._model_to_entity(user_model)
        return None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserEntity]:
        """获取所有用户（分页）"""
        stmt = select(UserModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()
        
        return [self._model_to_entity(user_model) for user_model in user_models]
    
    async def update(self, user: UserEntity) -> UserEntity:
        """更新用户"""
        stmt = update(UserModel).where(UserModel.id == user.id).values(
            username=user.username,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            updated_at=datetime.utcnow()
        )
        await self.session.execute(stmt)
        await self.session.commit()
        
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        """删除用户"""
        stmt = delete(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在"""
        stmt = select(func.count(UserModel.id)).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count > 0
    
    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在"""
        stmt = select(func.count(UserModel.id)).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count > 0
    
    async def exists_by_phone(self, phone: str) -> bool:
        """检查手机号是否存在"""
        stmt = select(func.count(UserModel.id)).where(UserModel.phone == phone)
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count > 0
    
    def _model_to_entity(self, user_model: UserModel) -> UserEntity:
        """将模型转换为实体"""
        return UserEntity(
            id=user_model.id,
            email=user_model.email,
            username=user_model.username,
            hashed_password=user_model.hashed_password,
            phone=user_model.phone,
            is_active=user_model.is_active,
            is_superuser=user_model.is_superuser,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            last_login=user_model.last_login
        )


class PostgreSQLLayerRepository(LayerRepository):
    """PostgreSQL图层仓储实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, layer: Layer) -> Layer:
        """创建图层"""
        layer_model = LayerModel(
            name=layer.name,
            description=layer.description,
            geometry_type=layer.geometry_type.value,
            srid=layer.srid,
            extent_min_x=layer.extent.min_x if layer.extent else None,
            extent_min_y=layer.extent.min_y if layer.extent else None,
            extent_max_x=layer.extent.max_x if layer.extent else None,
            extent_max_y=layer.extent.max_y if layer.extent else None,
            feature_count=layer.feature_count,
            is_visible=layer.is_visible,
            opacity=layer.opacity,
            style=layer.style
        )
        
        self.session.add(layer_model)
        await self.session.commit()
        await self.session.refresh(layer_model)
        
        return self._model_to_entity(layer_model)
    
    async def get_by_id(self, layer_id: UUID) -> Optional[Layer]:
        """根据ID获取图层"""
        stmt = select(LayerModel).where(LayerModel.id == layer_id)
        result = await self.session.execute(stmt)
        layer_model = result.scalar_one_or_none()
        
        if layer_model:
            return self._model_to_entity(layer_model)
        return None
    
    async def get_by_name(self, name: str) -> Optional[Layer]:
        """根据名称获取图层"""
        stmt = select(LayerModel).where(LayerModel.name == name)
        result = await self.session.execute(stmt)
        layer_model = result.scalar_one_or_none()
        
        if layer_model:
            return self._model_to_entity(layer_model)
        return None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Layer]:
        """获取所有图层"""
        stmt = select(LayerModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        layer_models = result.scalars().all()
        
        return [self._model_to_entity(layer_model) for layer_model in layer_models]
    
    async def update(self, layer: Layer) -> Layer:
        """更新图层"""
        stmt = update(LayerModel).where(LayerModel.id == layer.id).values(
            name=layer.name,
            description=layer.description,
            geometry_type=layer.geometry_type.value,
            srid=layer.srid,
            extent_min_x=layer.extent.min_x if layer.extent else None,
            extent_min_y=layer.extent.min_y if layer.extent else None,
            extent_max_x=layer.extent.max_x if layer.extent else None,
            extent_max_y=layer.extent.max_y if layer.extent else None,
            feature_count=layer.feature_count,
            is_visible=layer.is_visible,
            opacity=layer.opacity,
            style=layer.style,
            updated_at=datetime.utcnow()
        )
        await self.session.execute(stmt)
        await self.session.commit()
        
        return layer
    
    async def delete(self, layer_id: UUID) -> bool:
        """删除图层"""
        stmt = delete(LayerModel).where(LayerModel.id == layer_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def update_extent(self, layer_id: UUID, extent: SpatialExtent) -> bool:
        """更新图层空间范围"""
        stmt = update(LayerModel).where(LayerModel.id == layer_id).values(
            extent_min_x=extent.min_x,
            extent_min_y=extent.min_y,
            extent_max_x=extent.max_x,
            extent_max_y=extent.max_y,
            updated_at=datetime.utcnow()
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def update_feature_count(self, layer_id: UUID, count: int) -> bool:
        """更新图层要素数量"""
        stmt = update(LayerModel).where(LayerModel.id == layer_id).values(
            feature_count=count,
            updated_at=datetime.utcnow()
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    def _model_to_entity(self, layer_model: LayerModel) -> Layer:
        """将模型转换为实体"""
        extent = None
        if layer_model.extent_min_x is not None:
            extent = SpatialExtent(
                min_x=layer_model.extent_min_x,
                min_y=layer_model.extent_min_y,
                max_x=layer_model.extent_max_x,
                max_y=layer_model.extent_max_y,
                srid=layer_model.srid
            )
        
        return Layer(
            id=layer_model.id,
            name=layer_model.name,
            description=layer_model.description,
            geometry_type=GeometryType(layer_model.geometry_type),
            srid=layer_model.srid,
            extent=extent,
            feature_count=layer_model.feature_count,
            is_visible=layer_model.is_visible,
            opacity=layer_model.opacity,
            style=layer_model.style,
            created_at=layer_model.created_at,
            updated_at=layer_model.updated_at
        )


class PostgreSQLSpatialFeatureRepository(SpatialFeatureRepository):
    """PostgreSQL空间要素仓储实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, feature: SpatialFeature) -> SpatialFeature:
        """创建空间要素"""
        feature_model = SpatialFeatureModel(
            layer_id=feature.layer_id,
            geometry=feature.geometry.wkt,
            properties=feature.properties
        )
        
        self.session.add(feature_model)
        await self.session.commit()
        await self.session.refresh(feature_model)
        
        return self._model_to_entity(feature_model)
    
    async def get_by_id(self, feature_id: UUID) -> Optional[SpatialFeature]:
        """根据ID获取空间要素"""
        stmt = select(SpatialFeatureModel).where(SpatialFeatureModel.id == feature_id)
        result = await self.session.execute(stmt)
        feature_model = result.scalar_one_or_none()
        
        if feature_model:
            return self._model_to_entity(feature_model)
        return None
    
    async def get_by_layer_id(self, layer_id: UUID, skip: int = 0, limit: int = 1000) -> List[SpatialFeature]:
        """根据图层ID获取空间要素"""
        stmt = select(SpatialFeatureModel).where(
            SpatialFeatureModel.layer_id == layer_id
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        feature_models = result.scalars().all()
        
        return [self._model_to_entity(feature_model) for feature_model in feature_models]
    
    async def get_by_extent(self, layer_id: UUID, extent: SpatialExtent) -> List[SpatialFeature]:
        """根据空间范围获取要素"""
        # 使用PostGIS的空间查询
        stmt = text("""
            SELECT * FROM spatial_features 
            WHERE layer_id = :layer_id 
            AND ST_Intersects(geometry, ST_MakeEnvelope(:min_x, :min_y, :max_x, :max_y, :srid))
        """)
        
        result = await self.session.execute(stmt, {
            "layer_id": str(layer_id),
            "min_x": extent.min_x,
            "min_y": extent.min_y,
            "max_x": extent.max_x,
            "max_y": extent.max_y,
            "srid": extent.srid
        })
        
        feature_models = result.fetchall()
        return [self._model_to_entity_from_row(row) for row in feature_models]
    
    async def get_by_geometry_type(self, layer_id: UUID, geometry_type: GeometryType) -> List[SpatialFeature]:
        """根据几何类型获取要素"""
        # 使用PostGIS的几何类型查询
        stmt = text("""
            SELECT * FROM spatial_features 
            WHERE layer_id = :layer_id 
            AND ST_GeometryType(geometry) = :geometry_type
        """)
        
        result = await self.session.execute(stmt, {
            "layer_id": str(layer_id),
            "geometry_type": f"ST_{geometry_type.value}"
        })
        
        feature_models = result.fetchall()
        return [self._model_to_entity_from_row(row) for row in feature_models]
    
    async def update(self, feature: SpatialFeature) -> SpatialFeature:
        """更新空间要素"""
        stmt = update(SpatialFeatureModel).where(SpatialFeatureModel.id == feature.id).values(
            geometry=feature.geometry.wkt,
            properties=feature.properties,
            updated_at=datetime.utcnow()
        )
        await self.session.execute(stmt)
        await self.session.commit()
        
        return feature
    
    async def delete(self, feature_id: UUID) -> bool:
        """删除空间要素"""
        stmt = delete(SpatialFeatureModel).where(SpatialFeatureModel.id == feature_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def delete_by_layer_id(self, layer_id: UUID) -> bool:
        """删除图层的所有要素"""
        stmt = delete(SpatialFeatureModel).where(SpatialFeatureModel.layer_id == layer_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def count_by_layer_id(self, layer_id: UUID) -> int:
        """统计图层要素数量"""
        stmt = select(func.count(SpatialFeatureModel.id)).where(
            SpatialFeatureModel.layer_id == layer_id
        )
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def get_extent_by_layer_id(self, layer_id: UUID) -> Optional[SpatialExtent]:
        """获取图层空间范围"""
        stmt = text("""
            SELECT 
                ST_XMin(ST_Extent(geometry)) as min_x,
                ST_YMin(ST_Extent(geometry)) as min_y,
                ST_XMax(ST_Extent(geometry)) as max_x,
                ST_YMax(ST_Extent(geometry)) as max_y
            FROM spatial_features 
            WHERE layer_id = :layer_id
        """)
        
        result = await self.session.execute(stmt, {"layer_id": str(layer_id)})
        row = result.fetchone()
        
        if row and row[0] is not None:
            return SpatialExtent(
                min_x=row[0],
                min_y=row[1],
                max_x=row[2],
                max_y=row[3],
                srid=4326
            )
        return None
    
    def _model_to_entity(self, feature_model: SpatialFeatureModel) -> SpatialFeature:
        """将模型转换为实体"""
        geometry = loads(feature_model.geometry)
        
        return SpatialFeature(
            id=feature_model.id,
            geometry=geometry,
            properties=feature_model.properties,
            layer_id=feature_model.layer_id,
            created_at=feature_model.created_at,
            updated_at=feature_model.updated_at
        )
    
    def _model_to_entity_from_row(self, row) -> SpatialFeature:
        """从查询行转换为实体"""
        geometry = loads(row.geometry)
        
        return SpatialFeature(
            id=row.id,
            geometry=geometry,
            properties=row.properties,
            layer_id=row.layer_id,
            created_at=row.created_at,
            updated_at=row.updated_at
        )


class PostgreSQLAnalysisResultRepository(AnalysisResultRepository):
    """PostgreSQL分析结果仓储实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, result: AnalysisResult) -> AnalysisResult:
        """创建分析结果"""
        result_model = AnalysisResultModel(
            analysis_type=result.analysis_type.value,
            input_parameters=result.input_parameters,
            result_data=result.result_data,
            geometry=result.geometry.wkt if result.geometry else None,
            statistics=result.statistics,
            execution_time=result.execution_time
        )
        
        self.session.add(result_model)
        await self.session.commit()
        await self.session.refresh(result_model)
        
        return self._model_to_entity(result_model)
    
    async def get_by_id(self, result_id: UUID) -> Optional[AnalysisResult]:
        """根据ID获取分析结果"""
        stmt = select(AnalysisResultModel).where(AnalysisResultModel.id == result_id)
        result = await self.session.execute(stmt)
        result_model = result.scalar_one_or_none()
        
        if result_model:
            return self._model_to_entity(result_model)
        return None
    
    async def get_by_analysis_type(self, analysis_type: AnalysisType, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """根据分析类型获取结果"""
        stmt = select(AnalysisResultModel).where(
            AnalysisResultModel.analysis_type == analysis_type.value
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        result_models = result.scalars().all()
        
        return [self._model_to_entity(result_model) for result_model in result_models]
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """获取所有分析结果"""
        stmt = select(AnalysisResultModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        result_models = result.scalars().all()
        
        return [self._model_to_entity(result_model) for result_model in result_models]
    
    async def delete(self, result_id: UUID) -> bool:
        """删除分析结果"""
        stmt = delete(AnalysisResultModel).where(AnalysisResultModel.id == result_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def delete_by_analysis_type(self, analysis_type: AnalysisType) -> bool:
        """删除指定类型的分析结果"""
        stmt = delete(AnalysisResultModel).where(
            AnalysisResultModel.analysis_type == analysis_type.value
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    def _model_to_entity(self, result_model: AnalysisResultModel) -> AnalysisResult:
        """将模型转换为实体"""
        geometry = None
        if result_model.geometry:
            geometry = loads(result_model.geometry)
        
        return AnalysisResult(
            id=result_model.id,
            analysis_type=AnalysisType(result_model.analysis_type),
            input_parameters=result_model.input_parameters,
            result_data=result_model.result_data,
            geometry=geometry,
            statistics=result_model.statistics,
            execution_time=result_model.execution_time,
            created_at=result_model.created_at
        )


class PostgreSQLSpatialQueryRepository(SpatialQueryRepository):
    """PostgreSQL空间查询仓储实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def execute_spatial_query(self, query: SpatialQuery) -> List[SpatialFeature]:
        """执行空间查询"""
        if not query.spatial_filter:
            return []
        
        # 根据空间过滤条件构建查询
        filter_type = query.spatial_filter.get("type")
        geometry_wkt = query.spatial_filter.get("geometry")
        
        if not geometry_wkt:
            return []
        
        geometry = loads(geometry_wkt)
        
        if filter_type == "intersects":
            return await self.find_features_intersecting(
                query.query_parameters.get("layer_id"), geometry
            )
        elif filter_type == "within":
            return await self.find_features_within(
                query.query_parameters.get("layer_id"), geometry
            )
        elif filter_type == "contains":
            return await self.find_features_containing(
                query.query_parameters.get("layer_id"), geometry
            )
        elif filter_type == "distance":
            distance = query.spatial_filter.get("distance", 0)
            return await self.find_features_within_distance(
                query.query_parameters.get("layer_id"), geometry, distance
            )
        
        return []
    
    async def execute_attribute_query(self, query: SpatialQuery) -> List[SpatialFeature]:
        """执行属性查询"""
        if not query.attribute_filter:
            return []
        
        layer_id = query.query_parameters.get("layer_id")
        if not layer_id:
            return []
        
        # 构建属性过滤条件
        conditions = []
        params = {"layer_id": str(layer_id)}
        
        for key, value in query.attribute_filter.items():
            conditions.append(f"properties->>'{key}' = :{key}")
            params[key] = str(value)
        
        where_clause = " AND ".join(conditions)
        
        stmt = text(f"""
            SELECT * FROM spatial_features 
            WHERE layer_id = :layer_id AND {where_clause}
            LIMIT :limit OFFSET :offset
        """)
        
        params.update({
            "limit": query.limit,
            "offset": query.offset
        })
        
        result = await self.session.execute(stmt, params)
        rows = result.fetchall()
        
        return [self._row_to_feature(row) for row in rows]
    
    async def execute_sql_query(self, query: SpatialQuery) -> List[Dict[str, Any]]:
        """执行SQL查询"""
        if not query.sql_query:
            return []
        
        stmt = text(query.sql_query)
        result = await self.session.execute(stmt)
        rows = result.fetchall()
        
        return [dict(row._mapping) for row in rows]
    
    async def execute_hybrid_query(self, query: SpatialQuery) -> List[SpatialFeature]:
        """执行混合查询"""
        # 先执行空间查询
        spatial_features = await self.execute_spatial_query(query)
        
        # 如果有属性过滤，进一步过滤
        if query.attribute_filter:
            filtered_features = []
            for feature in spatial_features:
                match = True
                for key, value in query.attribute_filter.items():
                    if feature.properties.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_features.append(feature)
            return filtered_features
        
        return spatial_features
    
    async def find_features_within_distance(
        self,
        layer_id: UUID,
        geometry: BaseGeometry,
        distance: float
    ) -> List[SpatialFeature]:
        """查找指定距离内的要素"""
        stmt = text("""
            SELECT * FROM spatial_features 
            WHERE layer_id = :layer_id 
            AND ST_DWithin(geometry, ST_GeomFromText(:geometry_wkt, 4326), :distance)
        """)
        
        result = await self.session.execute(stmt, {
            "layer_id": str(layer_id),
            "geometry_wkt": geometry.wkt,
            "distance": distance
        })
        
        rows = result.fetchall()
        return [self._row_to_feature(row) for row in rows]
    
    async def find_features_intersecting(
        self,
        layer_id: UUID,
        geometry: BaseGeometry
    ) -> List[SpatialFeature]:
        """查找相交的要素"""
        stmt = text("""
            SELECT * FROM spatial_features 
            WHERE layer_id = :layer_id 
            AND ST_Intersects(geometry, ST_GeomFromText(:geometry_wkt, 4326))
        """)
        
        result = await self.session.execute(stmt, {
            "layer_id": str(layer_id),
            "geometry_wkt": geometry.wkt
        })
        
        rows = result.fetchall()
        return [self._row_to_feature(row) for row in rows]
    
    async def find_features_containing(
        self,
        layer_id: UUID,
        geometry: BaseGeometry
    ) -> List[SpatialFeature]:
        """查找包含指定几何的要素"""
        stmt = text("""
            SELECT * FROM spatial_features 
            WHERE layer_id = :layer_id 
            AND ST_Contains(geometry, ST_GeomFromText(:geometry_wkt, 4326))
        """)
        
        result = await self.session.execute(stmt, {
            "layer_id": str(layer_id),
            "geometry_wkt": geometry.wkt
        })
        
        rows = result.fetchall()
        return [self._row_to_feature(row) for row in rows]
    
    async def find_features_within(
        self,
        layer_id: UUID,
        geometry: BaseGeometry
    ) -> List[SpatialFeature]:
        """查找在指定几何内的要素"""
        stmt = text("""
            SELECT * FROM spatial_features 
            WHERE layer_id = :layer_id 
            AND ST_Within(geometry, ST_GeomFromText(:geometry_wkt, 4326))
        """)
        
        result = await self.session.execute(stmt, {
            "layer_id": str(layer_id),
            "geometry_wkt": geometry.wkt
        })
        
        rows = result.fetchall()
        return [self._row_to_feature(row) for row in rows]
    
    def _row_to_feature(self, row) -> SpatialFeature:
        """将查询行转换为空间要素"""
        geometry = loads(row.geometry)
        
        return SpatialFeature(
            id=row.id,
            geometry=geometry,
            properties=row.properties,
            layer_id=row.layer_id,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
