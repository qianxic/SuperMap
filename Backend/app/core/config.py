"""
配置管理模块
统一管理所有系统配置
"""
from functools import lru_cache
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    app_name: str = "SuperMap GIS + AI Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # API 配置
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8080")
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        # 保持原始字符串格式，在属性中处理转换
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """获取解析后的 CORS origins 列表"""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(',')]
        return self.cors_origins
    
    # 数据库配置
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")  # 根据您的Navicat配置
    postgres_password: str = Field(default="001117", alias="POSTGRES_PASSWORD")  # 您的实际密码
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="supermap_gis", alias="POSTGRES_DB")  # 目标数据库
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # SuperMap 配置
    supermap_base_url: str = "http://localhost:8090"
    supermap_server_url: str = "http://localhost:8090"
    supermap_username: str = "admin"
    supermap_password: str = "admin"

    # JWT 配置
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 日志配置
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 全局配置实例
settings = get_settings()