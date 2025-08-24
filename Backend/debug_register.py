#!/usr/bin/env python3
"""
调试用户注册问题
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_register():
    """调试用户注册问题"""
    print("🔍 开始调试用户注册问题...")
    
    try:
        # 1. 测试数据库连接
        print("\n1. 测试数据库连接...")
        from app.core.database import engine
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ 数据库连接成功: {version}")
        
        # 2. 检查数据库表是否存在
        print("\n2. 检查数据库表...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
            tables = result.fetchall()
            print(f"✅ 数据库表: {[table[0] for table in tables]}")
            
            if 'users' not in [table[0] for table in tables]:
                print("❌ users表不存在，需要创建表")
                return
        
        # 3. 测试模型导入
        print("\n3. 测试模型导入...")
        from app.infrastructure.database.postgres.models import UserModel
        print("✅ UserModel导入成功")
        
        # 4. 测试仓储导入
        print("\n4. 测试仓储导入...")
        from app.infrastructure.database.postgres.repositories import PostgreSQLUserRepository
        print("✅ PostgreSQLUserRepository导入成功")
        
        # 5. 测试用例导入
        print("\n5. 测试用例导入...")
        from app.application.use_cases.user.auth_use_case import AuthUseCase
        print("✅ AuthUseCase导入成功")
        
        # 6. 测试DTO导入
        print("\n6. 测试DTO导入...")
        from app.application.dto.user_dto import UserRegisterDTO
        print("✅ UserRegisterDTO导入成功")
        
        print("\n✅ 所有导入测试通过")
        
    except Exception as e:
        print(f"❌ 调试过程中发现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_register())
