from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from datetime import datetime

class WorkflowState(TypedDict):
    """State for the N8N workflow"""
    messages: Annotated[List[Dict[str, Any]], add_messages]
    user_id: str
    topic: Optional[str]
    blog_content: Optional[str]
    theme: Optional[str]
    themed_blog: Optional[str]
    twitter_thread: Optional[str]
    hashnode_post: Optional[Dict[str, Any]]
    twitter_post: Optional[Dict[str, Any]]
    publish_schedule: Optional[Dict[str, Any]]
    workflow_status: str
    current_node: str
    human_input: Optional[str]
    hashnode_approval: Optional[str]
    twitter_approval: Optional[str]

class WorkflowRequest(BaseModel):
    user_id: str
    topic: str
    theme: Optional[str] = None
    schedule_twitter: Optional[datetime] = None
    schedule_hashnode: Optional[datetime] = None

class HumanInputRequest(BaseModel):
    thread_id: str
    user_input: str
    action: str  # "approve" or "reject"

class WorkflowResponse(BaseModel):
    thread_id: str
    status: str
    current_node: str
    message: str
    requires_human_input: bool 