"""
SuperMap客户端模块
实现与SuperMap iServer的通信
"""
import httpx
import json
from typing import Dict, List, Optional, Any
from app.core.config import settings


class SuperMapClient:
    """SuperMap客户端"""
    
    def __init__(self):
        self.base_url = settings.supermap_base_url
        self.username = settings.supermap_username
        self.password = settings.supermap_password
        self.client = httpx.AsyncClient(
            timeout=30.0,
            auth=(self.username, self.password)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def get_map_info(self, map_name: str) -> Dict[str, Any]:
        """获取地图信息"""
        url = f"{self.base_url}/iserver/services/map-{map_name}/rest/maps/{map_name}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    async def get_layers(self, map_name: str) -> List[Dict[str, Any]]:
        """获取图层列表"""
        url = f"{self.base_url}/iserver/services/map-{map_name}/rest/maps/{map_name}/layers"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    async def get_layer_info(self, map_name: str, layer_name: str) -> Dict[str, Any]:
        """获取图层信息"""
        url = f"{self.base_url}/iserver/services/map-{map_name}/rest/maps/{map_name}/layers/{layer_name}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    async def query_features(
        self,
        map_name: str,
        layer_name: str,
        geometry: Optional[Dict[str, Any]] = None,
        attribute_filter: Optional[str] = None,
        spatial_query_mode: str = "INTERSECT"
    ) -> List[Dict[str, Any]]:
        """查询要素"""
        url = f"{self.base_url}/iserver/services/map-{map_name}/rest/maps/{map_name}/layers/{layer_name}/features"
        
        params = {
            "returnContent": True,
            "fromIndex": 0,
            "toIndex": 1000
        }
        
        if geometry:
            params["geometry"] = json.dumps(geometry)
            params["spatialQueryMode"] = spatial_query_mode
        
        if attribute_filter:
            params["attributeFilter"] = attribute_filter
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def buffer_analysis(
        self,
        geometry: Dict[str, Any],
        distance: float,
        unit: str = "METER"
    ) -> Dict[str, Any]:
        """缓冲区分析"""
        url = f"{self.base_url}/iserver/services/spatialAnalyst/restjsr/spatialanalyst/geometry/buffer"
        
        data = {
            "geometry": geometry,
            "distance": distance,
            "unit": unit
        }
        
        response = await self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    async def distance_analysis(
        self,
        source_geometry: Dict[str, Any],
        target_geometry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """距离分析"""
        url = f"{self.base_url}/iserver/services/spatialAnalyst/restjsr/spatialanalyst/geometry/distance"
        
        data = {
            "sourceGeometry": source_geometry,
            "targetGeometry": target_geometry
        }
        
        response = await self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    async def overlay_analysis(
        self,
        source_layer: str,
        overlay_layer: str,
        operation: str = "INTERSECT"
    ) -> Dict[str, Any]:
        """叠加分析"""
        url = f"{self.base_url}/iserver/services/spatialAnalyst/restjsr/spatialanalyst/overlay"
        
        data = {
            "sourceLayer": source_layer,
            "overlayLayer": overlay_layer,
            "operation": operation
        }
        
        response = await self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    async def create_layer(
        self,
        map_name: str,
        layer_name: str,
        layer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建图层"""
        url = f"{self.base_url}/iserver/services/map-{map_name}/rest/maps/{map_name}/layers"
        
        response = await self.client.post(url, json=layer_info)
        response.raise_for_status()
        return response.json()
    
    async def add_features(
        self,
        map_name: str,
        layer_name: str,
        features: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """添加要素"""
        url = f"{self.base_url}/iserver/services/map-{map_name}/rest/maps/{map_name}/layers/{layer_name}/features"
        
        data = {
            "features": features
        }
        
        response = await self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    async def update_features(
        self,
        map_name: str,
        layer_name: str,
        features: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """更新要素"""
        url = f"{self.base_url}/iserver/services/map-{map_name}/rest/maps/{map_name}/layers/{layer_name}/features"
        
        data = {
            "features": features
        }
        
        response = await self.client.put(url, json=data)
        response.raise_for_status()
        return response.json()
    
    async def delete_features(
        self,
        map_name: str,
        layer_name: str,
        feature_ids: List[str]
    ) -> Dict[str, Any]:
        """删除要素"""
        url = f"{self.base_url}/iserver/services/map-{map_name}/rest/maps/{map_name}/layers/{layer_name}/features"
        
        params = {
            "ids": ",".join(feature_ids)
        }
        
        response = await self.client.delete(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_map_image(
        self,
        map_name: str,
        bounds: Dict[str, float],
        width: int = 800,
        height: int = 600,
        format: str = "PNG"
    ) -> bytes:
        """获取地图图片"""
        url = f"{self.base_url}/iserver/services/map-{map_name}/rest/maps/{map_name}/image"
        
        params = {
            "bounds": json.dumps(bounds),
            "width": width,
            "height": height,
            "format": format
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.content


# 创建全局客户端实例
supermap_client = SuperMapClient()
