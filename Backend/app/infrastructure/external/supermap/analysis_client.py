"""
SuperMap 空间分析客户端
实现基于数据集的缓冲区、路径、服务区分析
"""
import requests
import json
from typing import Dict, Any, List, Optional
from app.core.config import settings


class AnalysisServiceError(Exception):
    """空间分析服务异常"""
    pass


class SuperMapAnalysisClient:
    """SuperMap 空间分析客户端 - 基于数据集分析"""
    
    def __init__(self):
        self.base_url = settings.supermap_iserver_url
        self.auth = (settings.supermap_username, settings.supermap_password)
        self.network_service = getattr(settings, 'supermap_network_service', 'services/networkanalyst-changchun/restjsr/networkanalyst')
        self.spatial_service = getattr(settings, 'supermap_spatial_service', 'services/spatialanalyst-changchun/restjsr/spatialanalyst')
        
        print(f"🔧 SuperMap客户端初始化:")
        print(f"  基础URL: {self.base_url}")
        print(f"  网络分析服务: {self.network_service}")
        print(f"  空间分析服务: {self.spatial_service}")
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """统一请求处理"""
        url = f"{self.base_url}/{endpoint}"
        print(f"🌐 发送请求到: {url}")
        print(f"📦 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                auth=self.auth,
                headers={"Content-Type": "application/json"},
                timeout=60  # 增加超时时间
            )
            print(f"📡 响应状态: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            print(f"✅ 响应成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        except requests.RequestException as e:
            print(f"❌ 请求失败: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"❌ 错误响应: {e.response.text}")
            raise AnalysisServiceError(f"SuperMap 服务调用失败: {str(e)}")
    
    def buffer_analysis(self, dataset: str, distance: float, 
                       end_type: str = "ROUND", filter_query: str = "SMID>0") -> Dict[str, Any]:
        """数据集缓冲区分析"""
        endpoint = f"{self.spatial_service}/buffer"
        
        payload = {
            "dataset": dataset,
            "filterQueryParameter": {
                "attributeFilter": filter_query
            },
            "bufferSetting": {
                "endType": end_type,
                "leftDistance": {"value": distance},
                "rightDistance": {"value": distance},
                "semicircleLineSegment": 10
            },
            "coordinateSystem": {
                "epsgCode": 4326
            }
        }
        return self._make_request(endpoint, payload)
    
    def shortest_path(self, dataset: str, start_point: Dict[str, Any], end_point: Dict[str, Any],
                     weight_name: str = "length") -> Dict[str, Any]:
        """数据集路径分析"""
        endpoint = f"{self.network_service}/path"
        
        payload = {
            "isAnalyzeById": False,
            "nodes": [start_point, end_point],
            "hasLeastEdgeCount": False,
            "parameter": {
                "resultSetting": {
                    "returnEdgeFeatures": True,
                    "returnEdgeGeometry": True,
                    "returnEdgeIDs": True,
                    "returnNodeFeatures": True,
                    "returnNodeGeometry": True,
                    "returnNodeIDs": True,
                    "returnPathGuides": True,
                    "returnRoutes": True
                },
                "weightFieldName": weight_name,
                "dataset": dataset
            }
        }
        return self._make_request(endpoint, payload)
    
    def service_area(self, dataset: str, center_point: Dict[str, Any], break_values: List[float],
                    weight_name: str = "length") -> Dict[str, Any]:
        """数据集服务区分析"""
        endpoint = f"{self.network_service}/servicearea"
        
        payload = {
            "centers": [center_point],
            "parameter": {
                "weightFieldName": weight_name,
                "isFromCenter": True,
                "breakValues": break_values,
                "returnEdgeFeatures": True,
                "returnEdgeGeometry": True,
                "returnNodeFeatures": True,
                "dataset": dataset
            }
        }
        return self._make_request(endpoint, payload)
