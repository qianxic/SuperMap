#!/usr/bin/env python3
"""
基于空间边界索引的空间数据查询服务
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
    
    def intersects(self, other: 'SpatialBounds') -> bool:
        """检查是否与另一个边界相交"""
        return not (self.east < other.west or 
                   self.west > other.east or 
                   self.south > other.north or 
                   self.north < other.south)
    
    def contains(self, other: 'SpatialBounds') -> bool:
        """检查是否包含另一个边界"""
        return (self.west <= other.west and 
                self.east >= other.east and 
                self.south <= other.south and 
                self.north >= other.north)


class GeometryType(Enum):
    """几何类型"""
    POINT = "point"
    LINE = "line"
    POLYGON = "polygon"


class SpatialQueryService:
    """空间查询服务"""
    
    def __init__(self):
        self.spatial_tables = {
            "建筑物面": GeometryType.POLYGON,
            "水系面": GeometryType.POLYGON,
            "武汉_市级": GeometryType.POLYGON,
            "武汉_县级": GeometryType.POLYGON,
            "公路": GeometryType.LINE,
            "铁路": GeometryType.LINE,
            "水系线": GeometryType.LINE,
            "学校": GeometryType.POINT,
            "医院": GeometryType.POINT,
            "居民地地名点": GeometryType.POINT
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
            
            # 构建查询SQL
            query = f"""
                SELECT 
                    smid,
                    smsdriw, smsdrin, smsdrie, smsdris,
                    smgeometry,
                    smarea,
                    smperimeter,
                    smlength,
                    name,
                    type,
                    objectid,
                    gb
                FROM sdx."{table_name}"
                WHERE smsdriw <= $1  -- 东边界
                  AND smsdrie >= $2  -- 西边界
                  AND smsdris <= $3  -- 北边界
                  AND smsdrin >= $4  -- 南边界
                ORDER BY smid
                LIMIT $5 OFFSET $6
            """
            
            # 执行查询
            rows = await conn.fetch(
                query,
                bounds.east,    # 东边界
                bounds.west,    # 西边界
                bounds.north,   # 北边界
                bounds.south,   # 南边界
                limit,
                offset
            )
            
            # 转换结果
            results = []
            for row in rows:
                result = dict(row)
                # 添加空间边界信息
                result['spatial_bounds'] = {
                    'west': row['smsdriw'],
                    'north': row['smsdrin'],
                    'east': row['smsdrie'],
                    'south': row['smsdris']
                }
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
            
            # 构建边界框
            bounds = SpatialBounds(
                west=x - tolerance,
                east=x + tolerance,
                north=y + tolerance,
                south=y - tolerance
            )
            
            # 对于点要素，直接查询坐标
            if self.spatial_tables.get(table_name) == GeometryType.POINT:
                query = f"""
                    SELECT 
                        smid,
                        smx, smy,
                        name,
                        objectid,
                        class,
                        pinyin,
                        gnid,
                        xzname
                    FROM sdx."{table_name}"
                    WHERE smx BETWEEN $1 AND $2
                      AND smy BETWEEN $3 AND $4
                    ORDER BY smid
                    LIMIT $5
                """
                rows = await conn.fetch(query, bounds.west, bounds.east, bounds.south, bounds.north, limit)
            else:
                # 对于线要素和面要素，使用边界框查询
                query = f"""
                    SELECT 
                        smid,
                        smsdriw, smsdrin, smsdrie, smsdris,
                        smgeometry,
                        smarea,
                        smperimeter,
                        smlength,
                        name,
                        type,
                        objectid,
                        gb
                    FROM sdx."{table_name}"
                    WHERE smsdriw <= $1
                      AND smsdrie >= $2
                      AND smsdris <= $3
                      AND smsdrin >= $4
                    ORDER BY smid
                    LIMIT $5
                """
                rows = await conn.fetch(query, bounds.east, bounds.west, bounds.north, bounds.south, limit)
            
            results = [dict(row) for row in rows]
            await conn.close()
            return results
            
        except Exception as e:
            print(f"❌ 点查询失败: {e}")
            return []
    
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
    
    async def query_by_circle(
        self,
        table_name: str,
        center_x: float,
        center_y: float,
        radius: float,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """根据圆形范围查询数据"""
        bounds = SpatialBounds(
            west=center_x - radius,
            east=center_x + radius,
            north=center_y + radius,
            south=center_y - radius
        )
        
        # 先使用边界框过滤，然后在应用层进行精确的圆形过滤
        results = await self.query_by_bounds(table_name, bounds, limit)
        
        # 过滤出真正在圆内的要素（简化实现）
        filtered_results = []
        for result in results:
            if 'smsdriw' in result:  # 线要素或面要素
                # 检查边界框是否与圆相交
                if self._circle_intersects_bounds(center_x, center_y, radius, result):
                    filtered_results.append(result)
            elif 'smx' in result:  # 点要素
                # 检查点是否在圆内
                distance = ((result['smx'] - center_x) ** 2 + (result['smy'] - center_y) ** 2) ** 0.5
                if distance <= radius:
                    filtered_results.append(result)
        
        return filtered_results
    
    def _circle_intersects_bounds(
        self,
        center_x: float,
        center_y: float,
        radius: float,
        bounds: Dict[str, Any]
    ) -> bool:
        """检查圆是否与边界框相交"""
        # 计算边界框中心到圆心的最近距离
        closest_x = max(bounds['smsdriw'], min(center_x, bounds['smsdrie']))
        closest_y = max(bounds['smsdris'], min(center_y, bounds['smsdrin']))
        
        distance = ((closest_x - center_x) ** 2 + (closest_y - center_y) ** 2) ** 0.5
        return distance <= radius
    
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
            
            # 获取基本统计信息
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
            
            # 获取空间分布统计
            if stats:
                result = {
                    'table_name': table_name,
                    'total_count': stats['total_count'],
                    'spatial_extent': {
                        'west': stats['min_west'],
                        'east': stats['max_east'],
                        'south': stats['min_south'],
                        'north': stats['max_north']
                    },
                    'geometry_type': self.spatial_tables.get(table_name, 'unknown').value
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


async def demo_spatial_queries():
    """演示空间查询功能"""
    print("🔍 空间查询服务演示")
    print("=" * 50)
    
    service = SpatialQueryService()
    
    # 1. 获取可用表
    tables = await service.get_available_tables()
    print(f"📋 可用空间表: {', '.join(tables)}")
    
    # 2. 获取表统计信息
    print("\n📊 表统计信息:")
    for table in tables[:3]:  # 只显示前3个表
        stats = await service.get_table_statistics(table)
        if 'error' not in stats:
            print(f"   {table}: {stats['total_count']} 条记录")
            print(f"     空间范围: {stats['spatial_extent']}")
    
    # 3. 矩形范围查询示例
    print("\n🔍 矩形范围查询示例:")
    bounds = SpatialBounds(west=114.0, south=30.0, east=115.0, north=31.0)
    results = await service.query_by_bounds("学校", bounds, limit=5)
    print(f"   在指定范围内找到 {len(results)} 所学校")
    
    # 4. 点查询示例
    print("\n🔍 点查询示例:")
    point_results = await service.query_by_point("医院", 114.5, 30.5, tolerance=0.1, limit=3)
    print(f"   在点(114.5, 30.5)附近找到 {len(point_results)} 家医院")
    
    # 5. 圆形范围查询示例
    print("\n🔍 圆形范围查询示例:")
    circle_results = await service.query_by_circle("居民地地名点", 114.5, 30.5, 0.1, limit=5)
    print(f"   在圆形范围内找到 {len(circle_results)} 个居民地")
    
    print("\n✅ 空间查询演示完成！")


if __name__ == "__main__":
    asyncio.run(demo_spatial_queries())
