#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings
from app.infrastructure.database.postgres.models import Base


async def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
    # 创建数据库引擎
    engine = create_async_engine(
        settings.database_url,
        echo=True  # 显示SQL语句
    )
    
    try:
        # 创建所有表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ 数据库表创建成功！")
        
        # 验证连接
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"📊 PostgreSQL版本: {version}")
            
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        raise
    finally:
        await engine.dispose()


async def test_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    
    engine = create_async_engine(settings.database_url)
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1;"))
            print("✅ 数据库连接成功！")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("=" * 50)
    print("SuperMap GIS 数据库初始化工具")
    print("=" * 50)
    
    # 显示配置信息
    print(f"📋 数据库配置:")
    print(f"   主机: {settings.postgres_host}")
    print(f"   端口: {settings.postgres_port}")
    print(f"   数据库: {settings.postgres_db}")
    print(f"   用户: {settings.postgres_user}")
    print()
    
    # 测试连接
    asyncio.run(test_connection())
    print()
    
    # 初始化数据库
    asyncio.run(init_database())
    
    print("=" * 50)
    print("🎉 数据库初始化完成！")
    print("=" * 50)
