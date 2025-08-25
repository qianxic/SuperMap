#!/usr/bin/env python3
"""
基于空间边界索引的空间数据查询服务 (修正版)
"""
import asyncio
import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class SpatialBounds:
    """空间边界"""
    west: float
    north: float
    east: float
    south: float
    
    def __post_init__(self):
        """验证边界值"""
        if self.west >= self.east:
            raise ValueError("西边界必须小于东边界")
        if self.south >= self.north:
            raise ValueError("南边界必须小于北边界")


class GeometryType(Enum):
    """几何类型"""
    POINT = "point"
    LINE = "line"
    POLYGON = "polygon"


class SpatialQueryService:
    """空间查询服务"""
    
    def __init__(self):
        # 根据实际表结构定义查询字段
        self.spatial_tables = {
            "建筑物面": {
                "type": GeometryType.POLYGON,
                "bounds_fields": ["smsdriw", "smsdrin", "smsdrie", "smsdris"],
                "geometry_field": "smgeometry",
                "select_fields": ["smid", "smsdriw", "smsdrin", "smsdrie", "smsdris", "smgeometry", "smarea", "smperimeter", "name", "height"]
            },
            "水系面": {
                "type": GeometryType.POLYGON,
                "bounds_fields": ["smsdriw", "smsdrin", "smsdrie", "smsdris"],
                "geometry_field": "smgeometry",
                "select_fields": ["smid", "smsdriw", "smsdrin", "smsdrie", "smsdris", "smgeometry", "smarea", "smperimeter", "name", "hydc", "period"]
            },
            "武汉_市级": {
                "type": GeometryType.POLYGON,
                "bounds_fields": ["smsdriw", "smsdrin", "smsdrie", "smsdris"],
                "geometry_field": "smgeometry",
                "select_fields": ["smid", "smsdriw", "smsdrin", "smsdrie", "smsdris", "smgeometry", "smarea", "smperimeter", "name_1", "pac_1"]
            },
            "武汉_县级": {
                "type": GeometryType.POLYGON,
                "bounds_fields": ["smsdriw", "smsdrin", "smsdrie", "smsdris"],
                "geometry_field": "smgeometry",
                "select_fields": ["smid", "smsdriw", "smsdrin", "smsdrie", "smsdris", "smgeometry", "smarea", "smperimeter", "name_1", "pac_1"]
            },
            "公路": {
                "type": GeometryType.LINE,
                "bounds_fields": ["smsdriw", "smsdrin", "smsdrie", "smsdris"],
                "geometry_field": "smgeometry",
                "select_fields": ["smid", "smsdriw", "smsdrin", "smsdrie", "smsdris", "smgeometry", "smlength", "name", "type", "rn"]
            },
            "铁路": {
                "type": GeometryType.LINE,
                "bounds_fields": ["smsdriw", "smsdrin", "smsdrie", "smsdris"],
                "geometry_field": "smgeometry",
                "select_fields": ["smid", "smsdriw", "smsdrin", "smsdrie", "smsdris", "smgeometry", "smlength", "name", "type", "rn"]
            },
            "水系线": {
                "type": GeometryType.LINE,
                "bounds_fields": ["smsdriw", "smsdrin", "smsdrie", "smsdris"],
                "geometry_field": "smgeometry",
                "select_fields": ["smid", "smsdriw", "smsdrin", "smsdrie", "smsdris", "smgeometry", "smlength", "name", "hydc", "period"]
            },
            "学校": {
                "type": GeometryType.POINT,
                "bounds_fields": ["smx", "smy"],
                "geometry_field": None,
                "select_fields": ["smid", "smx", "smy", "name", "count"]
            },
            "医院": {
                "type": GeometryType.POINT,
                "bounds_fields": ["smx", "smy"],
                "geometry_field": None,
                "select_fields": ["smid", "smx", "smy", "name", "count"]
            },
            "居民地地名点": {
                "type": GeometryType.POINT,
                "bounds_fields": ["smx", "smy"],
                "geometry_field": None,
                "select_fields": ["smid", "smx", "smy", "name", "class", "pinyin", "gnid", "xzname"]
            }
        }
    
    async def query_by_bounds(
        self,
        table_name: str,
        bounds: SpatialBounds,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """根据空间边界查询数据"""
        try:
            from app.core.config import settings
            import asyncpg
            
            # 连接到数据库
            conn = await asyncpg.connect(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db
            )
            
            table_config = self.spatial_tables.get(table_name)
            if not table_config:
                raise ValueError(f"不支持的表: {table_name}")
            
            # 构建查询SQL
            select_fields = ", ".join(table_config["select_fields"])
            
            if table_config["type"] == GeometryType.POINT:
                # 点要素查询
                query = f"""
                    SELECT {select_fields}
                    FROM sdx."{table_name}"
                    WHERE smx BETWEEN $1 AND $2
                      AND smy BETWEEN $3 AND $4
                    ORDER BY smid
                    LIMIT $5 OFFSET $6
                """
                rows = await conn.fetch(
                    query,
                    bounds.west, bounds.east, bounds.south, bounds.north,
                    limit, offset
                )
            else:
                # 线要素和面要素查询
                query = f"""
                    SELECT {select_fields}
                    FROM sdx."{table_name}"
                    WHERE smsdriw <= $1  -- 东边界
                      AND smsdrie >= $2  -- 西边界
                      AND smsdris <= $3  -- 北边界
                      AND smsdrin >= $4  -- 南边界
                    ORDER BY smid
                    LIMIT $5 OFFSET $6
                """
                rows = await conn.fetch(
                    query,
                    bounds.east, bounds.west, bounds.north, bounds.south,
                    limit, offset
                )
            
            # 转换结果
            results = []
            for row in rows:
                result = dict(row)
                
                # 添加空间边界信息
                if table_config["type"] == GeometryType.POINT:
                    result['spatial_bounds'] = {
                        'x': row['smx'],
                        'y': row['smy']
                    }
                else:
                    result['spatial_bounds'] = {
                        'west': row['smsdriw'],
                        'north': row['smsdrin'],
                        'east': row['smsdrie'],
                        'south': row['smsdris']
                    }
                
                result['geometry_type'] = table_config["type"].value
                results.append(result)
            
            await conn.close()
            return results
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            return []
    
    async def query_by_point(
        self,
        table_name: str,
        x: float,
        y: float,
        tolerance: float = 0.001,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """根据点坐标查询附近的数据"""
        bounds = SpatialBounds(
            west=x - tolerance,
            east=x + tolerance,
            north=y + tolerance,
            south=y - tolerance
        )
        return await self.query_by_bounds(table_name, bounds, limit)
    
    async def query_by_rectangle(
        self,
        table_name: str,
        min_x: float,
        min_y: float,
        max_x: float,
        max_y: float,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """根据矩形范围查询数据"""
        bounds = SpatialBounds(west=min_x, south=min_y, east=max_x, north=max_y)
        return await self.query_by_bounds(table_name, bounds, limit)
    
    async def get_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """获取表的统计信息"""
        try:
            from app.core.config import settings
            import asyncpg
            
            conn = await asyncpg.connect(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db
            )
            
            table_config = self.spatial_tables.get(table_name)
            if not table_config:
                return {'table_name': table_name, 'error': 'Unsupported table'}
            
            # 根据表类型构建统计查询
            if table_config["type"] == GeometryType.POINT:
                stats_query = f"""
                    SELECT 
                        COUNT(*) as total_count,
                        MIN(smx) as min_x,
                        MAX(smx) as max_x,
                        MIN(smy) as min_y,
                        MAX(smy) as max_y
                    FROM sdx."{table_name}"
                """
            else:
                stats_query = f"""
                    SELECT 
                        COUNT(*) as total_count,
                        MIN(smsdriw) as min_west,
                        MAX(smsdrie) as max_east,
                        MIN(smsdris) as min_south,
                        MAX(smsdrin) as max_north
                    FROM sdx."{table_name}"
                """
            
            stats = await conn.fetchrow(stats_query)
            
            if stats:
                if table_config["type"] == GeometryType.POINT:
                    result = {
                        'table_name': table_name,
                        'total_count': stats['total_count'],
                        'spatial_extent': {
                            'min_x': stats['min_x'],
                            'max_x': stats['max_x'],
                            'min_y': stats['min_y'],
                            'max_y': stats['max_y']
                        },
                        'geometry_type': table_config["type"].value
                    }
                else:
                    result = {
                        'table_name': table_name,
                        'total_count': stats['total_count'],
                        'spatial_extent': {
                            'west': stats['min_west'],
                            'east': stats['max_east'],
                            'south': stats['min_south'],
                            'north': stats['max_north']
                        },
                        'geometry_type': table_config["type"].value
                    }
            else:
                result = {'table_name': table_name, 'error': 'No data found'}
            
            await conn.close()
            return result
            
        except Exception as e:
            return {'table_name': table_name, 'error': str(e)}
    
    async def get_available_tables(self) -> List[str]:
        """获取可用的空间表列表"""
        return list(self.spatial_tables.keys())
    
    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表的详细信息"""
        table_config = self.spatial_tables.get(table_name)
        if not table_config:
            return {'error': f'Table {table_name} not found'}
        
        return {
            'table_name': table_name,
            'geometry_type': table_config["type"].value,
            'bounds_fields': table_config["bounds_fields"],
            'geometry_field': table_config["geometry_field"],
            'select_fields': table_config["select_fields"]
        }


async def demo_spatial_queries():
    """演示空间查询功能"""
    print("🔍 空间查询服务演示 (修正版)")
    print("=" * 60)
    
    service = SpatialQueryService()
    
    # 1. 获取可用表
    tables = await service.get_available_tables()
    print(f"📋 可用空间表: {', '.join(tables)}")
    
    # 2. 获取表统计信息
    print("\n📊 表统计信息:")
    for table in ["学校", "医院", "建筑物面"]:
        stats = await service.get_table_statistics(table)
        if 'error' not in stats:
            print(f"   {table}: {stats['total_count']} 条记录")
            print(f"     空间范围: {stats['spatial_extent']}")
            print(f"     几何类型: {stats['geometry_type']}")
    
    # 3. 矩形范围查询示例 - 点要素
    print("\n🔍 矩形范围查询示例 (点要素):")
    bounds = SpatialBounds(west=114.0, south=30.0, east=115.0, north=31.0)
    results = await service.query_by_bounds("学校", bounds, limit=5)
    print(f"   在指定范围内找到 {len(results)} 所学校")
    if results:
        for i, school in enumerate(results[:3], 1):
            print(f"     {i}. {school.get('name', 'N/A')} (ID: {school['smid']})")
    
    # 4. 点查询示例
    print("\n🔍 点查询示例:")
    point_results = await service.query_by_point("医院", 114.5, 30.5, tolerance=0.1, limit=3)
    print(f"   在点(114.5, 30.5)附近找到 {len(point_results)} 家医院")
    if point_results:
        for i, hospital in enumerate(point_results[:3], 1):
            print(f"     {i}. {hospital.get('name', 'N/A')} (坐标: {hospital['smx']:.4f}, {hospital['smy']:.4f})")
    
    # 5. 矩形范围查询示例 - 面要素
    print("\n🔍 矩形范围查询示例 (面要素):")
    building_results = await service.query_by_bounds("建筑物面", bounds, limit=3)
    print(f"   在指定范围内找到 {len(building_results)} 个建筑物")
    if building_results:
        for i, building in enumerate(building_results[:3], 1):
            print(f"     {i}. {building.get('name', 'N/A')} (面积: {building.get('smarea', 0):.2f})")
    
    # 6. 线要素查询示例
    print("\n🔍 线要素查询示例:")
    road_results = await service.query_by_bounds("公路", bounds, limit=3)
    print(f"   在指定范围内找到 {len(road_results)} 条公路")
    if road_results:
        for i, road in enumerate(road_results[:3], 1):
            print(f"     {i}. {road.get('name', 'N/A')} (类型: {road.get('type', 'N/A')})")
    
    print("\n✅ 空间查询演示完成！")


if __name__ == "__main__":
    asyncio.run(demo_spatial_queries())
