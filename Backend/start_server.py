#!/usr/bin/env python3
"""
SuperMap GIS + AI Backend 启动脚本
包含依赖检查、数据库初始化和服务启动
"""
import asyncio
import sys
import os
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查依赖包是否安装"""
    print("🔍 检查依赖包...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'asyncpg',
        'alembic',
        'pydantic',
        'python-jose',
        'passlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True


async def test_database_connection():
    """测试数据库连接"""
    print("\n🔍 测试数据库连接...")
    
    try:
        from app.core.config import settings
        from app.core.database import engine
        
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ 数据库连接成功 - PostgreSQL {version}")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请检查:")
        print("  1. PostgreSQL服务是否启动")
        print("  2. 数据库配置是否正确")
        print("  3. 数据库supermap_gis是否存在")
        return False


async def init_database():
    """初始化数据库"""
    print("\n🚀 初始化数据库...")
    
    try:
        from app.core.config import settings
        from app.infrastructure.database.postgres.models import Base
        from app.core.database import engine
        
        # 创建所有表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ 数据库表创建成功")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False


def start_server():
    """启动服务器"""
    print("\n🚀 启动API服务器...")
    
    try:
        # 使用uvicorn启动服务器
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        print("\n📋 服务器信息:")
        print("  🌐 API地址: http://localhost:8000")
        print("  📚 API文档: http://localhost:8000/docs")
        print("  🔍 健康检查: http://localhost:8000/health")
        print("\n按 Ctrl+C 停止服务器")
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")


async def main():
    """主函数"""
    print("=" * 60)
    print("SuperMap GIS + AI Backend 启动工具")
    print("=" * 60)
    
    # 1. 检查依赖
    if not check_dependencies():
        return
    
    # 2. 测试数据库连接
    if not await test_database_connection():
        return
    
    # 3. 初始化数据库
    if not await init_database():
        return
    
    # 4. 启动服务器
    start_server()


if __name__ == "__main__":
    asyncio.run(main())
