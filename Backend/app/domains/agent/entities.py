"""
智能体领域 - 实体定义
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


class AgentType(Enum):
    """智能体类型"""
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    AGGREGATOR = "aggregator"


class AgentStatus(Enum):
    """智能体状态"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentEntity:
    """智能体实体"""
    id: UUID
    name: str
    agent_type: AgentType
    status: AgentStatus
    capabilities: List[str]
    current_task_id: Optional[UUID] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()


@dataclass
class TaskEntity:
    """任务实体"""
    id: UUID
    workflow_id: UUID
    agent_id: UUID
    task_type: str
    parameters: Dict[str, Any]
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()


@dataclass
class WorkflowEntity:
    """工作流实体"""
    id: UUID
    user_id: UUID
    name: str
    description: str
    tasks: List[TaskEntity]
    status: TaskStatus
    context: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    @classmethod
    def create_new(
        cls,
        user_id: UUID,
        name: str,
        description: str,
        context: Dict[str, Any]
    ) -> "WorkflowEntity":
        """创建新工作流"""
        return cls(
            id=uuid4(),
            user_id=user_id,
            name=name,
            description=description,
            tasks=[],
            status=TaskStatus.PENDING,
            context=context
        )
    
    def add_task(self, task: TaskEntity) -> None:
        """添加任务到工作流"""
        self.tasks.append(task)
        self.updated_at = datetime.utcnow()
    
    def update_status(self, status: TaskStatus) -> None:
        """更新工作流状态"""
        self.status = status
        self.updated_at = datetime.utcnow()


@dataclass
class ChatSessionEntity:
    """聊天会话实体"""
    id: UUID
    user_id: UUID
    messages: List[Dict[str, Any]]
    context: Dict[str, Any]
    workflow_ids: List[UUID]
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """添加消息到会话"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def update_context(self, key: str, value: Any) -> None:
        """更新会话上下文"""
        self.context[key] = value
        self.updated_at = datetime.utcnow()