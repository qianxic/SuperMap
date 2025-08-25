"""
PostgreSQL仓储实现
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime

from .models import UserModel
from app.domains.user.repositories import UserRepository
from app.domains.user.entities import UserEntity
from app.domains.gis.repositories import (
    LayerRepository, SpatialFeatureRepository, AnalysisResultRepository
)
from app.domains.gis.entities import (
    Layer, SpatialFeature, AnalysisResult, SpatialExtent, GeometryType, AnalysisType
)


class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL用户(users)仓储实现"""
    
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
    
    async def get_active_users(self) -> List[UserEntity]:
        """获取所有活跃用户"""
        stmt = select(UserModel).where(UserModel.is_active == True)
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()
        
        return [self._model_to_entity(user_model) for user_model in user_models]
    
    async def update(self, user_id: UUID, update_data: Dict[str, Any]) -> Optional[UserEntity]:
        """更新用户信息"""
        # 移除不允许更新的字段
        update_data.pop('id', None)
        update_data.pop('created_at', None)
        update_data['updated_at'] = datetime.utcnow()
        
        stmt = update(UserModel).where(UserModel.id == user_id).values(**update_data)
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        if result.rowcount > 0:
            return await self.get_by_id(user_id)
        return None
    
    async def update_last_login(self, user_id: UUID) -> bool:
        """更新最后登录时间"""
        stmt = update(UserModel).where(UserModel.id == user_id).values(
            last_login=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def delete(self, user_id: UUID) -> bool:
        """删除用户"""
        stmt = delete(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def soft_delete(self, user_id: UUID) -> bool:
        """软删除用户（设置is_active为False）"""
        stmt = update(UserModel).where(UserModel.id == user_id).values(
            is_active=False,
            updated_at=datetime.utcnow()
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在"""
        stmt = select(UserModel.id).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在"""
        stmt = select(UserModel.id).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def exists_by_phone(self, phone: str) -> bool:
        """检查手机号是否存在"""
        stmt = select(UserModel.id).where(UserModel.phone == phone)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def get_user_stats(self) -> Dict[str, int]:
        """获取用户统计信息"""
        # 总用户数
        total_stmt = select(UserModel.id)
        total_result = await self.session.execute(total_stmt)
        total_users = len(total_result.scalars().all())
        
        # 活跃用户数
        active_stmt = select(UserModel.id).where(UserModel.is_active == True)
        active_result = await self.session.execute(active_stmt)
        active_users = len(active_result.scalars().all())
        
        # 今日新增用户数
        today = datetime.utcnow().date()
        today_stmt = select(UserModel.id).where(
            UserModel.created_at >= today
        )
        today_result = await self.session.execute(today_stmt)
        new_users_today = len(today_result.scalars().all())
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "new_users_today": new_users_today
        }
    
    def _model_to_entity(self, user_model: UserModel) -> UserEntity:
        """将数据库模型转换为领域实体"""
        return UserEntity(
            id=user_model.id,  # type: ignore
            username=user_model.username,  # type: ignore
            email=user_model.email,  # type: ignore
            phone=user_model.phone,  # type: ignore
            hashed_password=user_model.hashed_password,  # type: ignore
            is_active=user_model.is_active,  # type: ignore
            is_superuser=user_model.is_superuser,  # type: ignore
            created_at=user_model.created_at,  # type: ignore
            updated_at=user_model.updated_at,  # type: ignore
            last_login=user_model.last_login  # type: ignore
        )


class PostgreSQLLayerRepository(LayerRepository):
    """PostgreSQL图层(layers)仓储实现
    
    注意: 此实现需要根据您实际制作的表结构进行调整
    当前为占位实现，等待表结构完成后进行完善
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, layer: Layer) -> Layer:
        """创建图层"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def get_by_id(self, layer_id: UUID) -> Optional[Layer]:
        """根据ID获取图层"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def get_by_name(self, name: str) -> Optional[Layer]:
        """根据名称获取图层"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Layer]:
        """获取所有图层"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def update(self, layer: Layer) -> Layer:
        """更新图层"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def delete(self, layer_id: UUID) -> bool:
        """删除图层"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def update_extent(self, layer_id: UUID, extent: SpatialExtent) -> bool:
        """更新图层空间范围"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def update_feature_count(self, layer_id: UUID, count: int) -> bool:
        """更新图层要素数量"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")


class PostgreSQLSpatialFeatureRepository(SpatialFeatureRepository):
    """PostgreSQL空间要素(spatial_features)仓储实现
    
    注意: 此实现需要根据您实际制作的表结构进行调整
    当前为占位实现，等待表结构完成后进行完善
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, feature: SpatialFeature) -> SpatialFeature:
        """创建空间要素"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def get_by_id(self, feature_id: UUID) -> Optional[SpatialFeature]:
        """根据ID获取空间要素"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def get_by_layer_id(self, layer_id: UUID, skip: int = 0, limit: int = 1000) -> List[SpatialFeature]:
        """根据图层ID获取空间要素"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def get_by_extent(self, layer_id: UUID, extent: SpatialExtent) -> List[SpatialFeature]:
        """根据空间范围获取要素"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def get_by_geometry_type(self, layer_id: UUID, geometry_type: GeometryType) -> List[SpatialFeature]:
        """根据几何类型获取要素"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def update(self, feature: SpatialFeature) -> SpatialFeature:
        """更新空间要素"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def delete(self, feature_id: UUID) -> bool:
        """删除空间要素"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def delete_by_layer_id(self, layer_id: UUID) -> bool:
        """删除图层的所有要素"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def count_by_layer_id(self, layer_id: UUID) -> int:
        """统计图层要素数量"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def get_extent_by_layer_id(self, layer_id: UUID) -> Optional[SpatialExtent]:
        """获取图层空间范围"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")


class PostgreSQLAnalysisResultRepository(AnalysisResultRepository):
    """PostgreSQL分析结果(analysis_results)仓储实现
    
    注意: 此实现需要根据您实际制作的表结构进行调整
    当前为占位实现，等待表结构完成后进行完善
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, result: AnalysisResult) -> AnalysisResult:
        """创建分析结果"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def get_by_id(self, result_id: UUID) -> Optional[AnalysisResult]:
        """根据ID获取分析结果"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def get_by_analysis_type(self, analysis_type: AnalysisType, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """根据分析类型获取结果"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """获取所有分析结果"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def delete(self, result_id: UUID) -> bool:
        """删除分析结果"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
    
    async def delete_by_analysis_type(self, analysis_type: AnalysisType) -> bool:
        """删除指定类型的分析结果"""
        # TODO: 根据实际表结构实现
        raise NotImplementedError("需要根据实际表结构实现")
