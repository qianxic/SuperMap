"""
GIS 领域服务
集成 SuperMap 实现基于数据集的空间分析功能
"""
from typing import Any, Dict, List, Optional
import pyproj
from pyproj import Transformer
from app.infrastructure.external.supermap.analysis_client import SuperMapAnalysisClient, AnalysisServiceError
from app.infrastructure.external.supermap.geometry_converter import SuperMapGeometryConverter
from app.core.config import settings


class DatasetManager:
    """数据集管理服务"""
    
    @staticmethod
    def get_buffer_dataset() -> str:
        """获取缓冲区分析数据集"""
        return settings.supermap_buffer_dataset
    
    @staticmethod
    def get_network_dataset() -> str:
        """获取网络分析数据集"""
        return settings.supermap_network_dataset
    
    @staticmethod
    def get_default_dataset() -> str:
        """获取默认数据集"""
        return settings.supermap_default_dataset


class GeometryProjector:
    """几何投影转换服务 - 武汉地区 UTM 50N"""
    
    def __init__(self):
        self.converter = SuperMapGeometryConverter()
        # 武汉位于东经114度左右，属于UTM 50N区带 (EPSG:32650)
        self.utm_zone = "EPSG:32650"  # UTM 50N
        self.wgs84 = "EPSG:4326"
        
        # 创建坐标转换器
        self.transformer_4326_to_utm = Transformer.from_crs(
            self.wgs84, self.utm_zone, always_xy=True
        )
        self.transformer_utm_to_4326 = Transformer.from_crs(
            self.utm_zone, self.wgs84, always_xy=True
        )
        
        print(f"🔧 坐标转换器初始化: WGS84 ↔ {self.utm_zone}")
    
    def to_metric(self, geojson: Dict[str, Any]) -> Dict[str, Any]:
        """4326 转 UTM 米制坐标系"""
        geom_type = geojson.get("type", "").lower()
        
        if geom_type == "point":
            coords = geojson["coordinates"]
            x, y = self.transformer_4326_to_utm.transform(coords[0], coords[1])
            return {
                "type": "Point",
                "coordinates": [x, y]
            }
        
        elif geom_type == "linestring":
            coords = geojson["coordinates"]
            transformed_coords = []
            for coord in coords:
                x, y = self.transformer_4326_to_utm.transform(coord[0], coord[1])
                transformed_coords.append([x, y])
            return {
                "type": "LineString",
                "coordinates": transformed_coords
            }
        
        elif geom_type == "polygon":
            coords = geojson["coordinates"]
            transformed_coords = []
            for ring in coords:
                ring_coords = []
                for coord in ring:
                    x, y = self.transformer_4326_to_utm.transform(coord[0], coord[1])
                    ring_coords.append([x, y])
                transformed_coords.append(ring_coords)
            return {
                "type": "Polygon",
                "coordinates": transformed_coords
            }
        
        elif geom_type == "multipoint":
            coords = geojson["coordinates"]
            transformed_coords = []
            for coord in coords:
                x, y = self.transformer_4326_to_utm.transform(coord[0], coord[1])
                transformed_coords.append([x, y])
            return {
                "type": "MultiPoint",
                "coordinates": transformed_coords
            }
        
        elif geom_type == "multilinestring":
            coords = geojson["coordinates"]
            transformed_coords = []
            for line in coords:
                line_coords = []
                for coord in line:
                    x, y = self.transformer_4326_to_utm.transform(coord[0], coord[1])
                    line_coords.append([x, y])
                transformed_coords.append(line_coords)
            return {
                "type": "MultiLineString",
                "coordinates": transformed_coords
            }
        
        elif geom_type == "multipolygon":
            coords = geojson["coordinates"]
            transformed_coords = []
            for poly in coords:
                poly_coords = []
                for ring in poly:
                    ring_coords = []
                    for coord in ring:
                        x, y = self.transformer_4326_to_utm.transform(coord[0], coord[1])
                        ring_coords.append([x, y])
                    poly_coords.append(ring_coords)
                transformed_coords.append(poly_coords)
            return {
                "type": "MultiPolygon",
                "coordinates": transformed_coords
            }
        
        else:
            raise ValueError(f"不支持的几何类型: {geom_type}")
    
    def to_wgs84(self, geojson: Dict[str, Any]) -> Dict[str, Any]:
        """UTM 米制转 4326"""
        geom_type = geojson.get("type", "").lower()
        
        if geom_type == "point":
            coords = geojson["coordinates"]
            x, y = self.transformer_utm_to_4326.transform(coords[0], coords[1])
            return {
                "type": "Point",
                "coordinates": [x, y]
            }
        
        elif geom_type == "linestring":
            coords = geojson["coordinates"]
            transformed_coords = []
            for coord in coords:
                x, y = self.transformer_utm_to_4326.transform(coord[0], coord[1])
                transformed_coords.append([x, y])
            return {
                "type": "LineString",
                "coordinates": transformed_coords
            }
        
        elif geom_type == "polygon":
            coords = geojson["coordinates"]
            transformed_coords = []
            for ring in coords:
                ring_coords = []
                for coord in ring:
                    x, y = self.transformer_utm_to_4326.transform(coord[0], coord[1])
                    ring_coords.append([x, y])
                transformed_coords.append(ring_coords)
            return {
                "type": "Polygon",
                "coordinates": transformed_coords
            }
        
        elif geom_type == "multipoint":
            coords = geojson["coordinates"]
            transformed_coords = []
            for coord in coords:
                x, y = self.transformer_utm_to_4326.transform(coord[0], coord[1])
                transformed_coords.append([x, y])
            return {
                "type": "MultiPoint",
                "coordinates": transformed_coords
            }
        
        elif geom_type == "multilinestring":
            coords = geojson["coordinates"]
            transformed_coords = []
            for line in coords:
                line_coords = []
                for coord in line:
                    x, y = self.transformer_utm_to_4326.transform(coord[0], coord[1])
                    line_coords.append([x, y])
                transformed_coords.append(line_coords)
            return {
                "type": "MultiLineString",
                "coordinates": transformed_coords
            }
        
        elif geom_type == "multipolygon":
            coords = geojson["coordinates"]
            transformed_coords = []
            for poly in coords:
                poly_coords = []
                for ring in poly:
                    ring_coords = []
                    for coord in ring:
                        x, y = self.transformer_utm_to_4326.transform(coord[0], coord[1])
                        ring_coords.append([x, y])
                    poly_coords.append(ring_coords)
                transformed_coords.append(poly_coords)
            return {
                "type": "MultiPolygon",
                "coordinates": transformed_coords
            }
        
        else:
            raise ValueError(f"不支持的几何类型: {geom_type}")
    
    def centroid_point(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """取几何质心"""
        return self.converter.get_centroid(feature["geometry"])
    
    def area_km2(self, polygon_geojson: Dict[str, Any]) -> float:
        """计算面积（平方千米）- 使用 UTM 投影精确计算"""
        try:
            # 先转换到 UTM 坐标系进行面积计算
            utm_geom = self.to_metric(polygon_geojson)
            
            # 计算面积（平方米）
            area_m2 = self._calculate_area_m2(utm_geom)
            
            # 转换为平方千米
            area_km2 = area_m2 / 1_000_000.0
            
            print(f"📐 面积计算: {area_m2:.2f} m² = {area_km2:.6f} km²")
            return area_km2
            
        except Exception as e:
            print(f"⚠️ 面积计算失败，使用默认值: {e}")
            return 0.0
    
    def _calculate_area_m2(self, geojson: Dict[str, Any]) -> float:
        """计算几何面积（平方米）"""
        geom_type = geojson.get("type", "").lower()
        
        if geom_type == "polygon":
            return self._polygon_area(geojson["coordinates"][0])
        
        elif geom_type == "multipolygon":
            total_area = 0.0
            for poly_coords in geojson["coordinates"]:
                total_area += self._polygon_area(poly_coords[0])
            return total_area
        
        else:
            raise ValueError(f"不支持的面积计算几何类型: {geom_type}")
    
    def _polygon_area(self, coords: List[List[float]]) -> float:
        """使用 Shoelace 公式计算多边形面积"""
        if len(coords) < 3:
            return 0.0
        
        area = 0.0
        n = len(coords)
        
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]
        
        return abs(area) / 2.0


class BufferService:
    """缓冲区分析服务 - 基于数据集"""
    
    def __init__(self):
        self.supermap_client = SuperMapAnalysisClient()
        self.converter = SuperMapGeometryConverter()
        self.projector = GeometryProjector()
    
    def buffer_geojson(self, input_geojson: Dict[str, Any], distance_m: float, 
                      cap_style: str, dissolve: bool) -> Dict[str, Any]:
        """缓冲区分析占位实现"""
        raise NotImplementedError("BufferService.buffer_geojson is not implemented")


class RoutingService:
    """路径分析服务 - 基于数据集"""
    
    def __init__(self):
        self.supermap_client = SuperMapAnalysisClient()
        self.converter = SuperMapGeometryConverter()
        self.projector = GeometryProjector()
    
    def shortest_path(self, start_feature: Dict[str, Any], end_feature: Dict[str, Any], 
                     profile: str, weight: str) -> Dict[str, Any]:
        """最优路径分析占位实现"""
        raise NotImplementedError("RoutingService.shortest_path is not implemented")
    
    def _get_centroid(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """获取几何质心"""
        if feature["geometry"]["type"] == "Point":
            return feature["geometry"]
        return self.projector.centroid_point(feature)
    
    def _empty_route_result(self, profile: str, weight: str) -> Dict[str, Any]:
        """空路径结果"""
        return {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": []},
            "properties": {
                "length_km": 0.0,
                "duration_min": 0.0,
                "profile": profile,
                "weight": weight,
                "source": "supermap",
                "dataset": "RoadLine2@Changchun"
            }
        }


class IsochroneService:
    """等时圈分析服务 - 基于数据集"""
    
    def __init__(self):
        self.supermap_client = SuperMapAnalysisClient()
        self.converter = SuperMapGeometryConverter()
        self.projector = GeometryProjector()
    
    def isochrones(self, origin_feature: Dict[str, Any], mode: str, 
                  cutoff_min: int, bands: Optional[List[int]]) -> Dict[str, Any]:
        """等时圈分析占位实现"""
        raise NotImplementedError("IsochroneService.isochrones is not implemented")
    
    def _get_centroid(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """获取几何质心"""
        if feature["geometry"]["type"] == "Point":
            return feature["geometry"]
        return self.projector.centroid_point(feature)
            