#!/usr/bin/env python3
"""
API测试脚本
测试用户注册、登录和数据流入数据库
"""
import asyncio
import sys
import os
import httpx
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# API基础URL
BASE_URL = "http://localhost:8000"

# 测试用户数据
TEST_USER = {
    "username": f"testuser_{int(datetime.now().timestamp())}",
    "email": f"test_{int(datetime.now().timestamp())}@example.com",
    "phone": f"138{int(datetime.now().timestamp()) % 100000000:08d}",
    "password": "password123",
    "confirm_password": "password123"
}

async def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查成功: {data}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False


async def test_user_register():
    """测试用户注册"""
    print(f"\n🔍 测试用户注册: {TEST_USER['username']}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/user/register",
                json=TEST_USER,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 用户注册成功: {data}")
                return True
            else:
                print(f"❌ 用户注册失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 用户注册异常: {e}")
            return False


async def test_user_login():
    """测试用户登录"""
    print(f"\n🔍 测试用户登录: {TEST_USER['username']}...")
    
    login_data = {
        "login_identifier": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/user/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 用户登录成功: {data}")
                return data.get("token")
            else:
                print(f"❌ 用户登录失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 用户登录异常: {e}")
            return None


async def test_user_profile(token):
    """测试获取用户资料"""
    print(f"\n🔍 测试获取用户资料...")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{BASE_URL}/api/v1/user/profile",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取用户资料成功: {data}")
                return True
            else:
                print(f"❌ 获取用户资料失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取用户资料异常: {e}")
            return False


async def test_get_user_info(token):
    """测试获取当前用户信息"""
    print(f"\n🔍 测试获取当前用户信息...")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{BASE_URL}/api/v1/user/me",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取用户信息成功: {data}")
                return True
            else:
                print(f"❌ 获取用户信息失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取用户信息异常: {e}")
            return False


async def test_get_user_stats(token):
    """测试获取用户统计信息"""
    print(f"\n🔍 测试获取用户统计信息...")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{BASE_URL}/api/v1/user/stats",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取用户统计成功: {data}")
                return True
            else:
                print(f"❌ 获取用户统计失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取用户统计异常: {e}")
            return False


async def test_update_user_profile(token):
    """测试修改用户资料"""
    print(f"\n🔍 测试修改用户资料...")
    
    # 先获取当前用户信息
    current_user_info = None
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{BASE_URL}/api/v1/user/profile",
                headers=headers
            )
            
            if response.status_code == 200:
                current_user_info = response.json().get("data", {})
            else:
                print(f"❌ 获取当前用户信息失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 获取当前用户信息异常: {e}")
            return False
    
    # 准备更新数据
    update_data = {
        "old_username": current_user_info.get("username", ""),
        "new_username": current_user_info.get("username", ""),  # 保持不变
        "old_email": current_user_info.get("email", ""),
        "new_email": f"updated_{int(datetime.now().timestamp())}@example.com",
        "old_phone": current_user_info.get("phone", ""),
        "new_phone": f"139{int(datetime.now().timestamp()) % 100000000:08d}"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/user/update-profile",
                json=update_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 修改用户资料成功: {data}")
                return True
            else:
                print(f"❌ 修改用户资料失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 修改用户资料异常: {e}")
            return False


async def test_change_password(token):
    """测试修改密码"""
    print(f"\n🔍 测试修改密码...")
    
    password_data = {
        "current_password": TEST_USER["password"],
        "new_password": "newpassword123",
        "confirm_new_password": "newpassword123"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/user/change-password",
                json=password_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 修改密码成功: {data}")
                # 更新测试用户的密码
                TEST_USER["password"] = "newpassword123"
                return True
            else:
                print(f"❌ 修改密码失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 修改密码异常: {e}")
            return False


async def test_user_logout(token):
    """测试用户登出"""
    print(f"\n🔍 测试用户登出...")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/user/logout",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 用户登出成功: {data}")
                return True
            else:
                print(f"❌ 用户登出失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 用户登出异常: {e}")
            return False


async def test_database_verification():
    """验证数据库中的数据"""
    print(f"\n🔍 验证数据库中的数据...")
    
    try:
        from app.core.database import AsyncSessionLocal
        from app.infrastructure.database.postgres.models import UserModel
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            # 查询刚创建的用户
            stmt = select(UserModel).where(UserModel.username == TEST_USER["username"])
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                print(f"✅ 数据库验证成功:")
                print(f"  用户ID: {str(user.id)}")
                print(f"  用户名: {user.username}")
                print(f"  邮箱: {user.email}")
                print(f"  手机号: {user.phone}")
                print(f"  创建时间: {user.created_at}")
                return True
            else:
                print(f"❌ 数据库中未找到用户: {TEST_USER['username']}")
                return False
    except Exception as e:
        print(f"❌ 数据库验证异常: {e}")
        return False


async def main():
    """主测试函数"""
    print("=" * 60)
    print("SuperMap GIS + AI Backend 用户认证系统完整测试")
    print("=" * 60)
    
    test_results = {
        "health_check": False,
        "user_register": False,
        "user_login": False,
        "user_profile": False,
        "user_info": False,
        "user_stats": False,
        "update_profile": False,
        "change_password": False,
        "user_logout": False,
        "database_verification": False
    }
    
    # 1. 测试健康检查
    print("\n📋 测试步骤 1/10: 系统健康检查")
    test_results["health_check"] = await test_health_check()
    if not test_results["health_check"]:
        print("❌ 健康检查失败，请确保服务器正在运行")
        return
    
    # 2. 测试用户注册
    print("\n📋 测试步骤 2/10: 用户注册")
    test_results["user_register"] = await test_user_register()
    if not test_results["user_register"]:
        print("❌ 用户注册失败")
        return
    
    # 3. 测试用户登录
    print("\n📋 测试步骤 3/10: 用户登录")
    token = await test_user_login()
    if not token:
        print("❌ 用户登录失败")
        return
    test_results["user_login"] = True
    
    # 4. 测试获取用户资料
    print("\n📋 测试步骤 4/10: 获取用户资料")
    test_results["user_profile"] = await test_user_profile(token)
    if not test_results["user_profile"]:
        print("❌ 获取用户资料失败")
        return
    
    # 5. 测试获取当前用户信息
    print("\n📋 测试步骤 5/10: 获取当前用户信息")
    test_results["user_info"] = await test_get_user_info(token)
    if not test_results["user_info"]:
        print("❌ 获取用户信息失败")
        return
    
    # 6. 测试获取用户统计信息
    print("\n📋 测试步骤 6/10: 获取用户统计信息")
    test_results["user_stats"] = await test_get_user_stats(token)
    if not test_results["user_stats"]:
        print("❌ 获取用户统计失败")
        return
    
    # 7. 测试修改用户资料
    print("\n📋 测试步骤 7/10: 修改用户资料")
    test_results["update_profile"] = await test_update_user_profile(token)
    if not test_results["update_profile"]:
        print("❌ 修改用户资料失败")
        return
    
    # 8. 测试修改密码
    print("\n📋 测试步骤 8/10: 修改密码")
    test_results["change_password"] = await test_change_password(token)
    if not test_results["change_password"]:
        print("❌ 修改密码失败")
        return
    
    # 9. 测试用户登出
    print("\n📋 测试步骤 9/10: 用户登出")
    test_results["user_logout"] = await test_user_logout(token)
    if not test_results["user_logout"]:
        print("❌ 用户登出失败")
        return
    
    # 10. 验证数据库中的数据
    print("\n📋 测试步骤 10/10: 数据库验证")
    test_results["database_verification"] = await test_database_verification()
    if not test_results["database_verification"]:
        print("❌ 数据库验证失败")
        return
    
    # 测试结果统计
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print("\n" + "=" * 60)
    print("🎉 用户认证系统完整测试完成！")
    print("=" * 60)
    print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
    print(f"📈 成功率: {(passed_tests/total_tests)*100:.1f}%")
    print("\n✅ 已测试的API功能:")
    print("  ✅ 系统健康检查")
    print("  ✅ 用户注册 (POST /register)")
    print("  ✅ 用户登录 (POST /login)")
    print("  ✅ 获取用户资料 (GET /profile)")
    print("  ✅ 获取用户信息 (GET /me)")
    print("  ✅ 获取用户统计 (GET /stats)")
    print("  ✅ 修改用户资料 (POST /update-profile)")
    print("  ✅ 修改密码 (POST /change-password)")
    print("  ✅ 用户登出 (POST /logout)")
    print("  ✅ 数据库验证")
    print("\n🎯 用户认证系统 100% 功能测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
