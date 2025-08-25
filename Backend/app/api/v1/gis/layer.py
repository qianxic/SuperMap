"""
GIS图层管理API
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.application.use_cases.gis.layer_use_case import GISLayerUseCase
from app.domains.gis.repositories import LayerRepository
from app.infrastructure.database.postgres.repositories import PostgreSQLLayerRepository
from .gis_dto import LayerInfo, LayerListResponse, GISResponse

router = APIRouter()


# 请求模型
class CreateLayerRequest(BaseModel):
    """创建图层请求"""
    layer_name: str
    layer_type: str
    geometry_type: str
    description: Optional[str] = None
    spatial_reference: Optional[str] = "EPSG:4326"


class UpdateLayerRequest(BaseModel):
    """更新图层请求"""
    layer_name: Optional[str] = None
    description: Optional[str] = None
    is_visible: Optional[bool] = None


# 依赖注入
def get_layer_use_case(session = Depends(get_db)) -> GISLayerUseCase:
    """获取图层用例实例"""
    layer_repo = PostgreSQLLayerRepository(session)
    return GISLayerUseCase(layer_repo)


@router.get("/", response_model=LayerListResponse)
async def get_layers(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    layer_type: Optional[str] = Query(None, description="图层类型过滤"),
    geometry_type: Optional[str] = Query(None, description="几何类型过滤"),
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISLayerUseCase = Depends(get_layer_use_case)
) -> Dict[str, Any]:
    """获取图层列表"""
    try:
        result = await use_case.get_layers(
            skip=skip,
            limit=limit,
            layer_type=layer_type,
            geometry_type=geometry_type
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图层列表失败: {str(e)}"
        )


@router.get("/{layer_id}", response_model=GISResponse)
async def get_layer_by_id(
    layer_id: str,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISLayerUseCase = Depends(get_layer_use_case)
) -> Dict[str, Any]:
    """根据ID获取图层详情"""
    try:
        result = await use_case.get_layer_by_id(layer_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图层详情失败: {str(e)}"
        )


@router.post("/", response_model=GISResponse)
async def create_layer(
    request: CreateLayerRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISLayerUseCase = Depends(get_layer_use_case)
) -> Dict[str, Any]:
    """创建新图层"""
    try:
        result = await use_case.create_layer(
            layer_name=request.layer_name,
            layer_type=request.layer_type,
            geometry_type=request.geometry_type,
            description=request.description,
            spatial_reference=request.spatial_reference or "EPSG:4326",
            created_by=current_user_id
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建图层失败: {str(e)}"
        )


@router.put("/{layer_id}", response_model=GISResponse)
async def update_layer(
    layer_id: str,
    request: UpdateLayerRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISLayerUseCase = Depends(get_layer_use_case)
) -> Dict[str, Any]:
    """更新图层信息"""
    try:
        update_data = {}
        if request.layer_name is not None:
            update_data["layer_name"] = request.layer_name
        if request.description is not None:
            update_data["description"] = request.description
        if request.is_visible is not None:
            update_data["is_visible"] = request.is_visible
        
        result = await use_case.update_layer(
            layer_id=layer_id,
            update_data=update_data,
            updated_by=current_user_id
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新图层失败: {str(e)}"
        )


@router.delete("/{layer_id}", response_model=GISResponse)
async def delete_layer(
    layer_id: str,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISLayerUseCase = Depends(get_layer_use_case)
) -> Dict[str, Any]:
    """删除图层"""
    try:
        result = await use_case.delete_layer(
            layer_id=layer_id,
            deleted_by=current_user_id
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除图层失败: {str(e)}"
        )


@router.post("/{layer_id}/upload", response_model=GISResponse)
async def upload_layer_data(
    layer_id: str,
    file: UploadFile = File(..., description="上传的GIS数据文件"),
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISLayerUseCase = Depends(get_layer_use_case)
) -> Dict[str, Any]:
    """上传图层数据"""
    try:
        # 验证文件类型
        allowed_extensions = ['.shp', '.geojson', '.kml', '.gml', '.csv']
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件名不能为空"
            )
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        
        if f'.{file_extension}' not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {file_extension}。支持的类型: {', '.join(allowed_extensions)}"
            )
        
        # 读取文件内容
        file_content = await file.read()
        
        result = await use_case.upload_layer_data(
            layer_id=layer_id,
            file_name=file.filename,
            file_content=file_content,
            uploaded_by=current_user_id
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传图层数据失败: {str(e)}"
        )


@router.get("/{layer_id}/statistics", response_model=GISResponse)
async def get_layer_statistics(
    layer_id: str,
    current_user_id: str = Depends(get_current_user_id),
    use_case: GISLayerUseCase = Depends(get_layer_use_case)
) -> Dict[str, Any]:
    """获取图层统计信息"""
    try:
        result = await use_case.get_layer_statistics(layer_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图层统计信息失败: {str(e)}"
        )
