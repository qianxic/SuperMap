"""
异常处理模块
定义系统级异常类
"""


class AnalysisServiceError(Exception):
    """空间分析服务异常"""
    pass


class DatabaseError(Exception):
    """数据库操作异常"""
    pass


class ValidationError(Exception):
    """数据验证异常"""
    pass
