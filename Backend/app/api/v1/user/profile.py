"""
用户资料管理API
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dto.user_dto import UserUpdateDTO, PasswordChangeDTO
from app.application.use_cases.user.auth_use_case import AuthUseCase
from app.infrastructure.database.postgres.repositories import PostgreSQLUserRepository
from app.core.database import get_db
from app.core.security import get_current_user_id

router = APIRouter()


@router.get("/stats")
async def get_user_stats(
    session = Depends(get_db)
) -> Dict[str, Any]:
    """获取用户统计信息"""
    try:
        user_repository = PostgreSQLUserRepository(session)
        auth_use_case = AuthUseCase(user_repository)
        
        result = await auth_use_case.get_user_stats()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计信息失败"
        )


@router.post("/logout")
async def logout_user(
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """用户登出"""
    return {
        "success": True,
        "message": "登出成功，已清除用户会话"
    }


@router.post("/update-profile")
async def update_user_profile(
    user_data: UserUpdateDTO,
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """修改用户信息"""
    try:
        from uuid import UUID
        user_id = UUID(current_user_id)
        
        user_repository = PostgreSQLUserRepository(session)
        auth_use_case = AuthUseCase(user_repository)
        
        result = await auth_use_case.update_user_profile(user_id, user_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改用户信息失败"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeDTO,
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """修改密码"""
    try:
        from uuid import UUID
        user_id = UUID(current_user_id)
        
        user_repository = PostgreSQLUserRepository(session)
        auth_use_case = AuthUseCase(user_repository)
        
        result = await auth_use_case.change_password(user_id, password_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败"
        )
