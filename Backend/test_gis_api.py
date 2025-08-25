"""
GIS API 测试脚本
"""
import asyncio
import httpx
import json
from typing import Dict, Any


class GISAPITester:
    """GIS API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.auth_token = None
    
    async def login(self, username: str = "testuser", password: str = "testpass") -> bool:
        """登录获取认证令牌"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/user/auth/login",
                json={
                    "login_identifier": username,
                    "password": password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.auth_token = data["data"]["access_token"]
                    print("✅ 登录成功")
                    return True
            
            print(f"❌ 登录失败: {response.text}")
            return False
        except Exception as e:
            print(f"❌ 登录异常: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def test_create_layer(self) -> str:
        """测试创建图层"""
        try:
            layer_data = {
                "name": "测试图层",
                "description": "这是一个测试图层",
                "geometry_type": "Point",
                "srid": 4326
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/gis/layers/",
                json=layer_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    layer_id = data["data"]["id"]
                    print(f"✅ 创建图层成功: {layer_id}")
                    return layer_id
            
            print(f"❌ 创建图层失败: {response.text}")
            return None
        except Exception as e:
            print(f"❌ 创建图层异常: {str(e)}")
            return None
    
    async def test_create_feature(self, layer_id: str) -> str:
        """测试创建空间要素"""
        try:
            feature_data = {
                "layer_id": layer_id,
                "geometry_wkt": "POINT(116.3974 39.9093)",
                "properties": {
                    "name": "天安门",
                    "type": "landmark",
                    "description": "北京天安门广场"
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/gis/layers/{layer_id}/features",
                json=feature_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    feature_id = data["data"]["id"]
                    print(f"✅ 创建要素成功: {feature_id}")
                    return feature_id
            
            print(f"❌ 创建要素失败: {response.text}")
            return None
        except Exception as e:
            print(f"❌ 创建要素异常: {str(e)}")
            return None
    
    async def test_buffer_analysis(self, layer_id: str, geometry_id: str) -> str:
        """测试缓冲区分析"""
        try:
            analysis_data = {
                "layer_id": layer_id,
                "distance": 1000.0,
                "geometry_id": geometry_id
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/gis/analysis/buffer",
                json=analysis_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    analysis_id = data["data"]["analysis_id"]
                    print(f"✅ 缓冲区分析成功: {analysis_id}")
                    return analysis_id
            
            print(f"❌ 缓冲区分析失败: {response.text}")
            return None
        except Exception as e:
            print(f"❌ 缓冲区分析异常: {str(e)}")
            return None
    
    async def test_spatial_query(self, layer_id: str) -> bool:
        """测试空间查询"""
        try:
            query_data = {
                "layer_id": layer_id,
                "extent": {
                    "min_x": 116.0,
                    "min_y": 39.0,
                    "max_x": 117.0,
                    "max_y": 40.0,
                    "srid": 4326
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/gis/query/extent",
                json=query_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    features = data["data"]["features"]
                    print(f"✅ 空间查询成功，找到 {len(features)} 个要素")
                    return True
            
            print(f"❌ 空间查询失败: {response.text}")
            return False
        except Exception as e:
            print(f"❌ 空间查询异常: {str(e)}")
            return False
    
    async def test_get_layers(self) -> bool:
        """测试获取图层列表"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/gis/layers/",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    layers = data["data"]["layers"]
                    print(f"✅ 获取图层列表成功，共 {len(layers)} 个图层")
                    return True
            
            print(f"❌ 获取图层列表失败: {response.text}")
            return False
        except Exception as e:
            print(f"❌ 获取图层列表异常: {str(e)}")
            return False
    
    async def test_get_analysis_results(self) -> bool:
        """测试获取分析结果"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/gis/analysis/results?analysis_type=buffer",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    results = data["data"]["results"]
                    print(f"✅ 获取分析结果成功，共 {len(results)} 个结果")
                    return True
            
            print(f"❌ 获取分析结果失败: {response.text}")
            return False
        except Exception as e:
            print(f"❌ 获取分析结果异常: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始GIS API测试...")
        
        # 1. 登录
        if not await self.login():
            print("❌ 登录失败，无法继续测试")
            return
        
        # 2. 创建图层
        layer_id = await self.test_create_layer()
        if not layer_id:
            print("❌ 创建图层失败，无法继续测试")
            return
        
        # 3. 创建要素
        feature_id = await self.test_create_feature(layer_id)
        if not feature_id:
            print("❌ 创建要素失败，无法继续测试")
            return
        
        # 4. 缓冲区分析
        analysis_id = await self.test_buffer_analysis(layer_id, feature_id)
        
        # 5. 空间查询
        await self.test_spatial_query(layer_id)
        
        # 6. 获取图层列表
        await self.test_get_layers()
        
        # 7. 获取分析结果
        if analysis_id:
            await self.test_get_analysis_results()
        
        print("🎉 GIS API测试完成！")
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


async def main():
    """主函数"""
    tester = GISAPITester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())