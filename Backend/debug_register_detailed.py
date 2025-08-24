#!/usr/bin/env python3
"""
详细调试用户注册问题
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_register_detailed():
    """详细调试用户注册问题"""
    print("🔍 开始详细调试用户注册问题...")
    
    try:
        # 1. 测试数据库连接
        print("\n1. 测试数据库连接...")
        from app.core.database import engine
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ 数据库连接成功: {version}")
        
        # 2. 测试模型导入和表结构
        print("\n2. 测试模型导入...")
        from app.infrastructure.database.postgres.models import UserModel
        print("✅ UserModel导入成功")
        
        # 3. 测试仓储导入
        print("\n3. 测试仓储导入...")
        from app.infrastructure.database.postgres.repositories import PostgreSQLUserRepository
        print("✅ PostgreSQLUserRepository导入成功")
        
        # 4. 测试用例导入
        print("\n4. 测试用例导入...")
        from app.application.use_cases.user.auth_use_case import AuthUseCase
        print("✅ AuthUseCase导入成功")
        
        # 5. 测试DTO导入
        print("\n5. 测试DTO导入...")
        from app.application.dto.user_dto import UserRegisterDTO
        print("✅ UserRegisterDTO导入成功")
        
        # 6. 测试实体导入
        print("\n6. 测试实体导入...")
        from app.domains.user.entities import UserEntity
        print("✅ UserEntity导入成功")
        
        # 7. 测试完整的注册流程
        print("\n7. 测试完整的注册流程...")
        from app.core.database import get_db
        from app.application.dto.user_dto import UserRegisterDTO
        
        # 创建测试数据
        test_data = UserRegisterDTO(
            username="testuser_debug",
            email="test_debug@example.com",
            phone="13800138001",
            password="password123",
            confirm_password="password123"
        )
        
        print(f"✅ 测试数据创建成功: {test_data}")
        
        # 8. 测试数据库会话
        print("\n8. 测试数据库会话...")
        async for session in get_db():
            try:
                # 测试仓储创建
                user_repository = PostgreSQLUserRepository(session)
                print("✅ 用户仓储创建成功")
                
                # 测试用例创建
                auth_use_case = AuthUseCase(user_repository)
                print("✅ 认证用例创建成功")
                
                # 测试注册流程
                result = await auth_use_case.register_user(test_data)
                print(f"✅ 注册成功: {result}")
                break
                
            except Exception as e:
                print(f"❌ 注册过程中出错: {e}")
                import traceback
                traceback.print_exc()
                break
        
        print("\n✅ 所有测试通过")
        
    except Exception as e:
        print(f"❌ 调试过程中发现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_register_detailed())
