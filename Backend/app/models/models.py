from beanie import Document, Link
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class NodePosition(BaseModel):
    x: float
    y: float

class NodeData(BaseModel):
    id: str
    type: str
    position: NodePosition
    data: Dict[str, Any] = Field(default_factory=dict)

class EdgeData(BaseModel):
    id: str
    source: str
    target: str
    source_handle: Optional[str] = None
    target_handle: Optional[str] = None

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class User(Document):
    username: str = Field(...)
    email: str = Field(...)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            [("username", 1), {"unique": True}],
            [("email", 1), {"unique": True}],
        ]

class Workflow(Document):
    name: str = Field(...)
    description: Optional[str] = None
    nodes: List[NodeData] = Field(default_factory=list)
    edges: List[EdgeData] = Field(default_factory=list)
    is_active: bool = False
    owner_id: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "workflows"
        indexes = [
            [("owner_id", 1)],
            [("name", 1)],
            [("is_active", 1)],
        ]

class WorkflowExecution(Document):
    workflow_id: str = Field(...)
    status: ExecutionStatus = ExecutionStatus.PENDING
    current_node: Optional[str] = None
    execution_data: Dict[str, Any] = Field(default_factory=dict)
    results: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    thread_id: str = Field(...)
    user_id: str = Field(...)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "workflow_executions"
        indexes = [
            [("workflow_id", 1)],
            [("status", 1)],
            [("user_id", 1)],
            [("thread_id", 1)],
        ]

class NodeTemplate(Document):
    name: str = Field(...)
    category: str = Field(...)
    description: str
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    config_schema: Dict[str, Any] = Field(default_factory=dict)
    icon: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "node_templates"
        indexes = [
            [("category", 1)],
            [("name", 1), {"unique": True}],
        ]

class WorkflowCheckpoint(Document):
    thread_id: str = Field(...)
    checkpoint_id: str = Field(...)
    state: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "workflow_checkpoints"
        indexes = [
            [("thread_id", 1)],
            [("checkpoint_id", 1)],
        ]