#!/usr/bin/env python3
"""
测试配置值
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """测试配置值"""
    print("🔍 测试配置值...")
    
    try:
        from app.core.config import settings
        
        print(f"postgres_user: {settings.postgres_user}")
        print(f"postgres_password: {settings.postgres_password}")
        print(f"postgres_host: {settings.postgres_host}")
        print(f"postgres_port: {settings.postgres_port}")
        print(f"postgres_db: {settings.postgres_db}")
        print(f"database_url: {settings.database_url}")
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_config()
