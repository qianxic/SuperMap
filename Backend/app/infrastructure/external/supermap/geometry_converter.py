"""
SuperMap 几何格式转换器
实现 GeoJSON 与 SuperMap 格式的双向转换
"""
from typing import Dict, Any, List


class SuperMapGeometryConverter:
    """SuperMap 几何格式转换器"""
    
    @staticmethod
    def geojson_to_supermap(geojson: Dict[str, Any]) -> Dict[str, Any]:
        """GeoJSON 转 SuperMap 格式"""
        geom_type = geojson.get("type", "").lower()
        
        if geom_type == "point":
            coords = geojson["coordinates"]
            return {"x": coords[0], "y": coords[1]}
        
        elif geom_type == "linestring":
            points = [{"x": coord[0], "y": coord[1]} for coord in geojson["coordinates"]]
            return {"points": points}
        
        elif geom_type == "polygon":
            # 取外环
            coords = geojson["coordinates"][0]
            points = [{"x": coord[0], "y": coord[1]} for coord in coords]
            return {"points": points}
        
        elif geom_type == "multipoint":
            points = [{"x": coord[0], "y": coord[1]} for coord in geojson["coordinates"]]
            return {"points": points}
        
        elif geom_type == "multilinestring":
            line_strings = []
            for line_coords in geojson["coordinates"]:
                points = [{"x": coord[0], "y": coord[1]} for coord in line_coords]
                line_strings.append({"points": points})
            return {"lineStrings": line_strings}
        
        elif geom_type == "multipolygon":
            polygons = []
            for poly_coords in geojson["coordinates"]:
                # 取外环
                points = [{"x": coord[0], "y": coord[1]} for coord in poly_coords[0]]
                polygons.append({"points": points})
            return {"polygons": polygons}
        
        else:
            raise ValueError(f"不支持的几何类型: {geom_type}")
    
    @staticmethod
    def supermap_to_geojson(supermap_geom: Dict[str, Any]) -> Dict[str, Any]:
        """SuperMap 格式转 GeoJSON"""
        if "x" in supermap_geom and "y" in supermap_geom:
            # 点
            return {
                "type": "Point",
                "coordinates": [supermap_geom["x"], supermap_geom["y"]]
            }
        
        elif "points" in supermap_geom:
            # 线或面
            coords = [[p["x"], p["y"]] for p in supermap_geom["points"]]
            if len(coords) > 2 and coords[0] == coords[-1]:
                # 闭合，判断为面
                return {
                    "type": "Polygon",
                    "coordinates": [coords]
                }
            else:
                # 非闭合，判断为线
                return {
                    "type": "LineString",
                    "coordinates": coords
                }
        
        elif "lineStrings" in supermap_geom:
            # 多线
            coords = []
            for line in supermap_geom["lineStrings"]:
                line_coords = [[p["x"], p["y"]] for p in line["points"]]
                coords.append(line_coords)
            return {
                "type": "MultiLineString",
                "coordinates": coords
            }
        
        elif "polygons" in supermap_geom:
            # 多面
            coords = []
            for poly in supermap_geom["polygons"]:
                poly_coords = [[p["x"], p["y"]] for p in poly["points"]]
                coords.append([poly_coords])
            return {
                "type": "MultiPolygon",
                "coordinates": coords
            }
        
        else:
            raise ValueError(f"无法识别的 SuperMap 几何格式: {supermap_geom}")
    
    @staticmethod
    def get_centroid(geojson: Dict[str, Any]) -> Dict[str, Any]:
        """获取几何质心（简化实现）"""
        geom_type = geojson.get("type", "").lower()
        
        if geom_type == "point":
            return geojson
        
        elif geom_type == "linestring":
            coords = geojson["coordinates"]
            mid_idx = len(coords) // 2
            return {
                "type": "Point",
                "coordinates": coords[mid_idx]
            }
        
        elif geom_type == "polygon":
            coords = geojson["coordinates"][0]
            # 简化：取第一个点作为质心
            return {
                "type": "Point",
                "coordinates": coords[0]
            }
        
        else:
            # 其他类型简化处理
            return {
                "type": "Point",
                "coordinates": [0, 0]
            }
