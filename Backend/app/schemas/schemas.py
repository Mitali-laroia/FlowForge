from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.models.models import NodeData, EdgeData, ExecutionStatus

class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class WorkflowCreate(WorkflowBase):
    nodes: List[NodeData] = Field(default_factory=list)
    edges: List[EdgeData] = Field(default_factory=list)

class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    nodes: Optional[List[NodeData]] = None
    edges: Optional[List[EdgeData]] = None
    is_active: Optional[bool] = None

class WorkflowResponse(WorkflowBase):
    id: str
    nodes: List[NodeData]
    edges: List[EdgeData]
    is_active: bool
    owner_id: str
    created_at: datetime
    updated_at: datetime

class WorkflowExecutionCreate(BaseModel):
    input_data: Dict[str, Any] = Field(default_factory=dict)

class WorkflowExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: ExecutionStatus
    current_node: Optional[str]
    execution_data: Dict[str, Any]
    results: Dict[str, Any]
    error_message: Optional[str]
    thread_id: str
    user_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    last_updated: datetime

class UserInteractionRequest(BaseModel):
    execution_id: str
    decision: str = Field(..., pattern="^(yes|no)$")
    schedule_time: Optional[datetime] = None
    additional_data: Optional[Dict[str, Any]] = None

class NodeTemplateResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    config_schema: Dict[str, Any]
    icon: Optional[str]
    color: Optional[str]
    created_at: datetime

class ExecutionStatusUpdate(BaseModel):
    status: ExecutionStatus
    current_node: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None