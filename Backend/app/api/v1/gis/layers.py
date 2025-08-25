"""
GIS图层管理API
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.domains.gis.services import LayerManagementService
from app.domains.gis.repositories import LayerRepository, SpatialFeatureRepository
from app.infrastructure.database.postgres.repositories import (
    PostgreSQLLayerRepository, PostgreSQLSpatialFeatureRepository
)
from app.application.dto.gis_dto import (
    LayerCreateDTO, LayerUpdateDTO, LayerResponseDTO, 
    SpatialFeatureCreateDTO, SpatialFeatureResponseDTO
)

router = APIRouter()


# 依赖注入
def get_layer_service(session = Depends(get_db)) -> LayerManagementService:
    """获取图层管理服务实例"""
    layer_repo = PostgreSQLLayerRepository(session)
    feature_repo = PostgreSQLSpatialFeatureRepository(session)
    
    return LayerManagementService(layer_repo, feature_repo)


@router.post("/", response_model=Dict[str, Any])
async def create_layer(
    layer_data: LayerCreateDTO,
    current_user_id: str = Depends(get_current_user_id),
    layer_service: LayerManagementService = Depends(get_layer_service)
) -> Dict[str, Any]:
    """创建图层"""
    try:
        from app.domains.gis.entities import GeometryType
        
        # 验证几何类型
        try:
            geometry_type = GeometryType(layer_data.geometry_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的几何类型: {layer_data.geometry_type}"
            )
        
        layer = await layer_service.create_layer(
            name=layer_data.name,
            description=layer_data.description,
            geometry_type=geometry_type,
            srid=layer_data.srid
        )
        
        return {
            "success": True,
            "message": "图层创建成功",
            "data": layer.to_dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建图层失败: {str(e)}"
        )


@router.get("/", response_model=Dict[str, Any])
async def get_layers(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """获取图层列表"""
    try:
        layer_repo = PostgreSQLLayerRepository(session)
        layers = await layer_repo.get_all(skip, limit)
        
        return {
            "success": True,
            "message": "获取图层列表成功",
            "data": {
                "layers": [layer.to_dict() for layer in layers],
                "total": len(layers),
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图层列表失败: {str(e)}"
        )


@router.get("/{layer_id}", response_model=Dict[str, Any])
async def get_layer(
    layer_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """获取图层详情"""
    try:
        from uuid import UUID
        
        layer_repo = PostgreSQLLayerRepository(session)
        layer = await layer_repo.get_by_id(UUID(layer_id))
        
        if not layer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图层不存在"
            )
        
        return {
            "success": True,
            "message": "获取图层详情成功",
            "data": layer.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图层详情失败: {str(e)}"
        )


@router.put("/{layer_id}", response_model=Dict[str, Any])
async def update_layer(
    layer_id: str,
    layer_data: LayerUpdateDTO,
    current_user_id: str = Depends(get_current_user_id),
    layer_service: LayerManagementService = Depends(get_layer_service)
) -> Dict[str, Any]:
    """更新图层"""
    try:
        from uuid import UUID
        
        layer = await layer_service.update_layer_metadata(
            layer_id=UUID(layer_id),
            name=layer_data.name,
            description=layer_data.description,
            is_visible=layer_data.is_visible,
            opacity=layer_data.opacity,
            style=layer_data.style
        )
        
        return {
            "success": True,
            "message": "图层更新成功",
            "data": layer.to_dict()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新图层失败: {str(e)}"
        )


@router.delete("/{layer_id}", response_model=Dict[str, Any])
async def delete_layer(
    layer_id: str,
    current_user_id: str = Depends(get_current_user_id),
    layer_service: LayerManagementService = Depends(get_layer_service)
) -> Dict[str, Any]:
    """删除图层"""
    try:
        from uuid import UUID
        
        success = await layer_service.delete_layer(UUID(layer_id))
        
        if success:
            return {
                "success": True,
                "message": "图层删除成功",
                "data": {"layer_id": layer_id}
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图层不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除图层失败: {str(e)}"
        )


@router.get("/{layer_id}/statistics", response_model=Dict[str, Any])
async def get_layer_statistics(
    layer_id: str,
    current_user_id: str = Depends(get_current_user_id),
    layer_service: LayerManagementService = Depends(get_layer_service)
) -> Dict[str, Any]:
    """获取图层统计信息"""
    try:
        from uuid import UUID
        
        stats = await layer_service.calculate_layer_statistics(UUID(layer_id))
        
        return {
            "success": True,
            "message": "获取图层统计信息成功",
            "data": {
                "layer_id": layer_id,
                "statistics": stats
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图层统计信息失败: {str(e)}"
        )


@router.post("/{layer_id}/features", response_model=Dict[str, Any])
async def create_feature(
    layer_id: str,
    feature_data: SpatialFeatureCreateDTO,
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """创建空间要素"""
    try:
        from uuid import UUID
        from shapely.wkt import loads
        from app.domains.gis.entities import SpatialFeature
        
        # 验证图层存在
        layer_repo = PostgreSQLLayerRepository(session)
        layer = await layer_repo.get_by_id(UUID(feature_data.layer_id))
        if not layer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图层不存在"
            )
        
        # 解析几何
        try:
            geometry = loads(feature_data.geometry_wkt)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的几何WKT格式"
            )
        
        # 创建要素
        feature = SpatialFeature.create_new(
            geometry=geometry,
            properties=feature_data.properties,
            layer_id=UUID(feature_data.layer_id)
        )
        
        # 保存到数据库
        feature_repo = PostgreSQLSpatialFeatureRepository(session)
        created_feature = await feature_repo.create(feature)
        
        return {
            "success": True,
            "message": "空间要素创建成功",
            "data": created_feature.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建空间要素失败: {str(e)}"
        )


@router.get("/{layer_id}/features", response_model=Dict[str, Any])
async def get_layer_features(
    layer_id: str,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(1000, ge=1, le=10000, description="返回记录数"),
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """获取图层要素列表"""
    try:
        from uuid import UUID
        
        feature_repo = PostgreSQLSpatialFeatureRepository(session)
        features = await feature_repo.get_by_layer_id(UUID(layer_id), skip, limit)
        
        return {
            "success": True,
            "message": "获取图层要素列表成功",
            "data": {
                "layer_id": layer_id,
                "features": [feature.to_geojson() for feature in features],
                "total": len(features),
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图层要素列表失败: {str(e)}"
        )


@router.delete("/{layer_id}/features", response_model=Dict[str, Any])
async def delete_layer_features(
    layer_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """删除图层所有要素"""
    try:
        from uuid import UUID
        
        feature_repo = PostgreSQLSpatialFeatureRepository(session)
        success = await feature_repo.delete_by_layer_id(UUID(layer_id))
        
        return {
            "success": True,
            "message": "图层要素删除成功",
            "data": {"layer_id": layer_id}
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除图层要素失败: {str(e)}"
        )