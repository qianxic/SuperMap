"""
PostgreSQL 仓储实现
"""
from __future__ import annotations

from typing import Dict, List, Optional, Any, cast
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.entities import UserEntity
from app.domains.user.repositories import UserRepository
from app.infrastructure.database.postgres.models import UserModel, BufferResult, RouteResult, AccessibilityResult
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, cast
from shapely.geometry import shape
from geoalchemy2.shape import from_shape


def _model_to_entity(model: UserModel) -> UserEntity:
    return UserEntity(
        id=cast(UUID, model.id),
        email=cast(str, model.email),
        username=cast(str, model.username),
        hashed_password=cast(str, model.hashed_password),
        phone=cast(Optional[str], model.phone),
        is_active=cast(bool, model.is_active),
        is_superuser=cast(bool, model.is_superuser),
        created_at=cast(Optional[datetime], model.created_at),
        updated_at=cast(Optional[datetime], model.updated_at),
        last_login=cast(Optional[datetime], model.last_login),
    )


class PostgreSQLUserRepository(UserRepository):
    """基于 SQLAlchemy AsyncSession 的用户仓储实现"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserEntity) -> UserEntity:
        model = UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _model_to_entity(model)

    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        stmt = select(UserModel).where(UserModel.email == email.lower().strip())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        stmt = select(UserModel).where(UserModel.username == username.strip())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model else None

    async def get_by_phone(self, phone: str) -> Optional[UserEntity]:
        if not phone:
            return None
        stmt = select(UserModel).where(UserModel.phone == phone.strip())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model else None

    async def get_by_login_identifier(self, identifier: str) -> Optional[UserEntity]:
        identifier = identifier.strip()
        # username
        user = await self.get_by_username(identifier)
        if user:
            return user
        # email
        user = await self.get_by_email(identifier)
        if user:
            return user
        # phone
        return await self.get_by_phone(identifier)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserEntity]:
        stmt = select(UserModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [_model_to_entity(m) for m in models]

    async def get_active_users(self) -> List[UserEntity]:
        stmt = select(UserModel).where(UserModel.is_active.is_(True))
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [_model_to_entity(m) for m in models]

    async def update(self, user_id: UUID, update_data: Dict[str, Any]) -> Optional[UserEntity]:
        # 执行更新
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values({**update_data, "updated_at": func.now()})
            .returning(UserModel)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model else None

    async def update_last_login(self, user_id: UUID) -> bool:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(last_login=func.now(), updated_at=func.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def delete(self, user_id: UUID) -> bool:
        stmt = delete(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def soft_delete(self, user_id: UUID) -> bool:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_active=False, updated_at=func.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def exists_by_username(self, username: str) -> bool:
        stmt = select(func.count()).select_from(UserModel).where(UserModel.username == username.strip())
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(func.count()).select_from(UserModel).where(UserModel.email == email.lower().strip())
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def exists_by_phone(self, phone: str) -> bool:
        if not phone:
            return False
        stmt = select(func.count()).select_from(UserModel).where(UserModel.phone == phone.strip())
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def get_user_stats(self) -> Dict[str, int]:
        total_stmt = select(func.count()).select_from(UserModel)
        active_stmt = select(func.count()).select_from(UserModel).where(UserModel.is_active.is_(True))
        today = func.current_date()
        new_today_stmt = select(func.count()).select_from(UserModel).where(func.date(UserModel.created_at) == today)

        total = (await self.session.execute(total_stmt)).scalar_one()
        active = (await self.session.execute(active_stmt)).scalar_one()
        new_today = (await self.session.execute(new_today_stmt)).scalar_one()

        return {
            "total_users": int(total or 0),
            "active_users": int(active or 0),
            "new_users_today": int(new_today or 0),
        }



class AnalysisResultRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_buffer_result(self, req: Any, fc: Dict[str, Any]) -> int:
        """保存缓冲区分析结果"""
        area_km2 = 0.0
        geom_multi = None
        
        try:
            if fc.get("features"):
                area_km2 = float(fc["features"][0].get("properties", {}).get("area_km2", 0.0))
                # 转换几何为 PostGIS
                geom_multi = self._geojson_to_postgis(fc["features"][0]["geometry"])
        except Exception:
            area_km2 = 0.0
            geom_multi = None
        
        record = BufferResult(
            user_id=None,
            source_tag=None,
            input_json=getattr(req, "model_dump", lambda: req)(),
            result_fc_json=fc,
            buffer_m=getattr(req, "distance_m", None),
            cap_style=getattr(req, "cap_style", None),
            dissolved=getattr(req, "dissolve", None),
            geom=geom_multi,
            area_km2=area_km2,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return cast(int, record.id)

    def _geojson_to_postgis(self, geojson: Dict[str, Any]):
        """GeoJSON 转 PostGIS 几何"""
        try:
            if not geojson or geojson.get("type") == "Point":
                return None  # 点几何不存储
            shapely_geom = shape(geojson)
            return from_shape(shapely_geom, srid=4326)
        except Exception:
            return None

    async def save_route_result(self, req: Any, feat: Dict[str, Any]) -> int:
        """保存路径分析结果"""
        props = feat.get("properties", {})
        geom_line = None
        
        try:
            if feat.get("geometry"):
                geom_line = self._geojson_to_postgis(feat["geometry"])
        except Exception:
            geom_line = None
        
        record = RouteResult(
            user_id=None,
            source_tag=props.get("sourceTag"),
            input_json=getattr(req, "model_dump", lambda: req)(),
            result_feature_json=feat,
            profile=str(props.get("profile")) if props.get("profile") is not None else None,
            weight=str(props.get("weight")) if props.get("weight") is not None else None,
            length_km=float(props.get("length_km")) if props.get("length_km") is not None else None,
            duration_min=float(props.get("duration_min")) if props.get("duration_min") is not None else None,
            geom=geom_line,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return cast(int, record.id)

    async def save_accessibility_result(self, req: Any, fc: Dict[str, Any]) -> int:
        """保存可达性分析结果"""
        summary = fc.get("summary", {})
        geom_multi = None
        
        try:
            if fc.get("features"):
                # 合并所有等时圈几何
                from shapely.ops import unary_union
                polys = [shape(f["geometry"]) for f in fc["features"] if f.get("geometry")]
                if polys:
                    union = unary_union(polys)
                    geom_multi = from_shape(union, srid=4326)
        except Exception:
            geom_multi = None
        
        record = AccessibilityResult(
            user_id=None,
            source_tag=summary.get("sourceTag"),
            input_json=getattr(req, "model_dump", lambda: req)(),
            result_fc_json=fc,
            mode=str(summary.get("mode", getattr(req, "mode", None))) if summary.get("mode", getattr(req, "mode", None)) is not None else None,
            cutoff_min=int(getattr(req, "cutoff_min", 0)) if getattr(req, "cutoff_min", None) is not None else None,
            bands=getattr(req, "bands", None),
            total_area_km2=summary.get("total_area_km2"),
            geoms=geom_multi,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return cast(int, record.id)

