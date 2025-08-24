"""
用户领域值对象模块
"""
from dataclasses import dataclass
from typing import Optional
import re
from datetime import datetime


@dataclass(frozen=True)
class Email:
    """邮箱值对象"""
    value: str
    
    def __post_init__(self):
        if not self.validate(self.value):
            raise ValueError("邮箱格式不正确")
    
    @staticmethod
    def validate(email: str) -> bool:
        """验证邮箱格式"""
        if not email or '@' not in email:
            return False
        # 简单的邮箱格式验证
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def __str__(self) -> str:
        return self.value.lower().strip()
    
    def __repr__(self) -> str:
        return f"Email('{self.value}')"


@dataclass(frozen=True)
class Username:
    """用户名字值对象"""
    value: str
    
    def __post_init__(self):
        if not self.validate(self.value):
            raise ValueError("用户名格式不正确")
    
    @staticmethod
    def validate(username: str) -> bool:
        """验证用户名格式"""
        username = username.strip()
        return 2 <= len(username) <= 50
    
    def __str__(self) -> str:
        return self.value.strip()
    
    def __repr__(self) -> str:
        return f"Username('{self.value}')"


@dataclass(frozen=True)
class PhoneNumber:
    """手机号值对象"""
    value: Optional[str]
    
    def __post_init__(self):
        if self.value is not None and not self.validate(self.value):
            raise ValueError("手机号格式不正确")
    
    @staticmethod
    def validate(phone: str) -> bool:
        """验证手机号格式"""
        if not phone:
            return True  # 手机号可选
        phone = phone.strip()
        # 中国手机号验证：11位数字，以1开头
        return bool(re.match(r'^1[3-9]\d{9}$', phone))
    
    def __str__(self) -> str:
        return self.value.strip() if self.value else ""
    
    def __repr__(self) -> str:
        return f"PhoneNumber('{self.value}')" if self.value else "PhoneNumber(None)"


@dataclass(frozen=True)
class Password:
    """密码值对象"""
    value: str
    
    def __post_init__(self):
        if not self.validate(self.value):
            raise ValueError("密码格式不正确")
    
    @staticmethod
    def validate(password: str) -> bool:
        """验证密码强度"""
        return 6 <= len(password) <= 100
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return "Password('***')"  # 不暴露密码内容


@dataclass(frozen=True)
class UserId:
    """用户ID值对象"""
    value: str
    
    def __post_init__(self):
        if not self.validate(self.value):
            raise ValueError("用户ID格式不正确")
    
    @staticmethod
    def validate(user_id: str) -> bool:
        """验证用户ID格式"""
        # UUID格式验证
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, user_id.lower()))
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"UserId('{self.value}')"


@dataclass(frozen=True)
class UserStatus:
    """用户状态值对象"""
    is_active: bool
    is_superuser: bool
    
    def __post_init__(self):
        if not isinstance(self.is_active, bool):
            raise ValueError("is_active必须是布尔值")
        if not isinstance(self.is_superuser, bool):
            raise ValueError("is_superuser必须是布尔值")
    
    def can_login(self) -> bool:
        """检查用户是否可以登录"""
        return self.is_active
    
    def has_admin_privileges(self) -> bool:
        """检查用户是否有管理员权限"""
        return self.is_superuser
    
    def __repr__(self) -> str:
        return f"UserStatus(active={self.is_active}, superuser={self.is_superuser})"


@dataclass(frozen=True)
class Timestamp:
    """时间戳值对象"""
    value: datetime
    
    def __post_init__(self):
        if not isinstance(self.value, datetime):
            raise ValueError("时间戳必须是datetime类型")
    
    @classmethod
    def now(cls) -> "Timestamp":
        """创建当前时间戳"""
        return cls(datetime.utcnow())
    
    def to_iso_string(self) -> str:
        """转换为ISO格式字符串"""
        return self.value.isoformat()
    
    def __str__(self) -> str:
        return self.value.isoformat()
    
    def __repr__(self) -> str:
        return f"Timestamp('{self.value.isoformat()}')"
