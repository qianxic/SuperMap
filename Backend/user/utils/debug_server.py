#!/usr/bin/env python3
"""
SuperMap GIS + AI Backend 调试工具
诊断服务器连接和配置问题
"""
import asyncio
import sys
import os
import socket
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

def check_port_availability(host: str, port: int) -> bool:
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0  # 0表示端口被占用
    except Exception:
        return False

def check_process_on_port(port: int) -> list:
    """检查端口上的进程"""
    try:
        result = subprocess.run(
            ['netstat', '-ano'], 
            capture_output=True, 
            text=True, 
            shell=True
        )
        processes = []
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                processes.append(line.strip())
        return processes
    except Exception:
        return []

async def test_database_connection():
    """测试数据库连接"""
    print("\n🔍 测试数据库连接...")
    
    try:
        from user.core.config import settings
        print(f"📋 数据库配置:")
        print(f"   主机: {settings.postgres_host}")
        print(f"   端口: {settings.postgres_port}")
        print(f"   数据库: {settings.postgres_db}")
        print(f"   用户: {settings.postgres_user}")
        
        # 测试端口连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((settings.postgres_host, settings.postgres_port))
        sock.close()
        
        if result == 0:
            print("✅ PostgreSQL端口连接成功")
        else:
            print(f"❌ PostgreSQL端口连接失败 (错误码: {result})")
            return False
        
        # 测试数据库连接
        from user.core.database import engine
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ 数据库连接成功 - PostgreSQL {version}")
            return True
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_environment():
    """检查环境配置"""
    print("\n🔍 检查环境配置...")
    
    try:
        from user.core.config import settings
        print(f"📋 应用配置:")
        print(f"   应用名称: {settings.app_name}")
        print(f"   环境: {settings.environment}")
        print(f"   调试模式: {settings.debug}")
        print(f"   API前缀: {settings.api_v1_prefix}")
        print(f"   CORS Origins: {settings.cors_origins}")
        
        # 检查环境变量
        print(f"\n📋 环境变量:")
        env_vars = [
            'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_HOST', 
            'POSTGRES_PORT', 'POSTGRES_DB'
        ]
        for var in env_vars:
            value = os.getenv(var, '未设置')
            print(f"   {var}: {value}")
            
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")

def check_dependencies():
    
    
    return True

def check_server_status():
    """检查服务器状态"""
    print("\n🔍 检查服务器状态...")
    
    host = "localhost"
    port = 8000
    
    # 检查端口是否被占用
    if check_port_availability(host, port):
        print(f"✅ 端口 {port} 可用")
    else:
        print(f"❌ 端口 {port} 被占用")
        processes = check_process_on_port(port)
        if processes:
            print("占用进程:")
            for proc in processes:
                print(f"   {proc}")
    
    # 测试HTTP连接
    try:
        import requests
        response = requests.get(f"http://{host}:{port}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器响应正常")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except ImportError:
        print("⚠️  requests模块未安装，跳过HTTP测试")

async def main():
    """主函数"""
    print("=" * 60)
    print("SuperMap GIS + AI Backend 调试工具")
    print("=" * 60)
    
    # 1. 检查环境配置
    check_environment()
    
    # 2. 检查依赖包
    if not check_dependencies():
        return
    
    # 3. 测试数据库连接
    await test_database_connection()
    
    # 4. 检查服务器状态
    check_server_status()
    
    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
