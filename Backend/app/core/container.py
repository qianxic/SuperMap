"""
依赖注入容器模块
实现真正的依赖倒置，管理所有服务的生命周期
"""
from typing import Dict, Any
from app.domains.user.repositories import UserRepository, MockUserRepository
from app.domains.user.services import UserService
from app.application.use_cases.user.auth_use_case import AuthUseCase
from app.application.use_cases.user.profile_use_case import ProfileUseCase


class Container:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._configure_services()
    
    def _configure_services(self):
        """配置服务依赖"""
        # 仓储层
        self._services['user_repository'] = MockUserRepository()
        
        # 领域服务层
        self._services['user_service'] = UserService(
            user_repository=self._services['user_repository']
        )
        
        # 用例层
        self._services['auth_use_case'] = AuthUseCase(
            user_repository=self._services['user_repository']
        )
        
        self._services['profile_use_case'] = ProfileUseCase(
            user_repository=self._services['user_repository']
        )
    
    def get(self, service_name: str) -> Any:
        """获取服务实例"""
        if service_name not in self._services:
            raise ValueError(f"Service '{service_name}' not found")
        return self._services[service_name]
    
    def register(self, service_name: str, service_instance: Any):
        """注册服务实例"""
        self._services[service_name] = service_instance
    
    def replace_repository(self, repository_name: str, repository_instance: Any):
        """替换仓储实现（用于测试或切换数据库）"""
        if repository_name not in self._services:
            raise ValueError(f"Repository '{repository_name}' not found")
        
        # 更新仓储
        self._services[repository_name] = repository_instance
        
        # 重新配置依赖该仓储的服务
        if repository_name == 'user_repository':
            self._services['user_service'] = UserService(
                user_repository=repository_instance
            )
            self._services['auth_use_case'] = AuthUseCase(
                user_repository=repository_instance
            )
            self._services['profile_use_case'] = ProfileUseCase(
                user_repository=repository_instance
            )


# 全局容器实例
container = Container()


# 依赖注入函数
def get_user_repository() -> UserRepository:
    """获取用户仓储"""
    return container.get('user_repository')


def get_user_service() -> UserService:
    """获取用户服务"""
    return container.get('user_service')


def get_auth_use_case() -> AuthUseCase:
    """获取认证用例"""
    return container.get('auth_use_case')


def get_profile_use_case() -> ProfileUseCase:
    """获取资料管理用例"""
    return container.get('profile_use_case')
