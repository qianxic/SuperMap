"""
用户资料管理用例层
"""
from typing import Optional, List, Dict
from uuid import UUID
from fastapi import HTTPException, status
from app.domains.user.entities import UserEntity
from app.domains.user.repositories import UserRepository
from app.api.v1.user.user_dto import (
    UserProfileResponse,
    UserUpdateRequest,
    ApiResponse
)


class ProfileUseCase:
    """用户资料管理用例"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def get_user_profile(self, user_id: UUID) -> UserProfileResponse:
        """获取用户资料"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        profile_data = user.to_profile_dict()
        return UserProfileResponse(**profile_data)
    
    async def update_user_profile(
        self,
        user_id: UUID,
        request: UserUpdateRequest
    ) -> ApiResponse:
        """更新用户资料"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证原信息是否正确
        if (request.old_username != user.username or 
            request.old_email != user.email or
            request.old_phone != user.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原用户信息不匹配，请检查输入"
            )
        
        # 验证新用户名是否已存在
        if request.new_username and request.new_username != user.username:
            existing_user = await self.user_repository.get_by_username(request.new_username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="新用户名已存在"
                )
        
        # 验证新邮箱是否已存在
        if request.new_email and request.new_email != user.email:
            existing_user = await self.user_repository.get_by_email(request.new_email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="新邮箱已存在"
                )
        
        # 验证新手机号是否已存在
        if request.new_phone and request.new_phone != user.phone:
            existing_user = await self.user_repository.get_by_phone(request.new_phone)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="新手机号已存在"
                )
        
        # 更新用户资料
        user.update_profile(
            username=request.new_username,
            email=request.new_email,
            phone=request.new_phone
        )
        
        # 保存到仓储
        update_data = {
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "updated_at": user.updated_at
        }
        updated_user = await self.user_repository.update(user.id, update_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="用户信息更新失败"
            )
        
        return ApiResponse(
            success=True,
            message="用户信息修改成功",
            data={
                "old_info": {
                    "username": request.old_username,
                    "email": request.old_email,
                    "phone": request.old_phone
                },
                "new_info": {
                    "username": updated_user.username,
                    "email": updated_user.email,
                    "phone": updated_user.phone
                }
            }
        )
    
    async def get_user_stats(self) -> Dict:
        """获取用户统计信息"""
        return await self.user_repository.get_user_stats()
    
    async def get_user_by_identifier(self, identifier: str) -> Optional[UserProfileResponse]:
        """根据标识符获取用户（支持用户名/邮箱/手机号）"""
        # 尝试按用户名查找
        user = await self.user_repository.get_by_username(identifier)
        if user:
            return UserProfileResponse(**user.to_profile_dict())
        
        # 尝试按邮箱查找
        user = await self.user_repository.get_by_email(identifier)
        if user:
            return UserProfileResponse(**user.to_profile_dict())
        
        # 尝试按手机号查找
        user = await self.user_repository.get_by_phone(identifier)
        if user:
            return UserProfileResponse(**user.to_profile_dict())
        
        return None

