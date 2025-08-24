#!/usr/bin/env python3
"""
检查数据库连接和创建数据库
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def check_database():
    """检查数据库连接"""
    print("🔍 检查数据库连接...")
    
    try:
        from app.core.config import settings
        import asyncpg
        
        # 尝试连接到默认数据库
        print(f"尝试连接到: {settings.postgres_host}:{settings.postgres_port}")
        print(f"用户: {settings.postgres_user}")
        print(f"数据库: {settings.postgres_db}")
        print(f"完整URL: {settings.database_url}")
        
        # 连接到默认数据库
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database='postgres'
        )
        
        print("✅ 成功连接到PostgreSQL")
        
        # 检查目标数据库是否存在
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            settings.postgres_db
        )
        
        if result:
            print(f"✅ 数据库 {settings.postgres_db} 已存在")
        else:
            print(f"❌ 数据库 {settings.postgres_db} 不存在，正在创建...")
            await conn.execute(f"CREATE DATABASE {settings.postgres_db}")
            print(f"✅ 数据库 {settings.postgres_db} 创建成功")
        
        await conn.close()
        
        # 测试连接到目标数据库
        print(f"\n测试连接到目标数据库: {settings.postgres_db}")
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db
        )
        
        print("✅ 成功连接到目标数据库")
        
        # 检查表是否存在
        result = await conn.fetchval(
            "SELECT 1 FROM information_schema.tables WHERE table_name = 'users'"
        )
        
        if result:
            print("✅ users表已存在")
        else:
            print("❌ users表不存在，需要创建")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_database())
