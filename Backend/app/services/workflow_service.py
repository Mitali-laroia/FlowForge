from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_core.runnables import RunnableConfig
from ..workflows.workflow_graph import compile_workflow_with_checkpointer
from ..schemas.workflow_state import WorkflowState, WorkflowRequest, HumanInputRequest
from ..core.config import settings
import uuid
from typing import Dict, Any

class WorkflowService:
    def __init__(self):
        self.mongo_uri = settings.MONGODB_URL
    
    async def start_workflow(self, request: WorkflowRequest) -> Dict[str, Any]:
        """Start a new workflow"""
        with MongoDBSaver.from_conn_string(self.mongo_uri) as checkpointer:
            workflow = compile_workflow_with_checkpointer(checkpointer)
            
            # Generate unique thread ID
            thread_id = str(uuid.uuid4())
            
            # Initialize state
            initial_state = WorkflowState(
                messages=[],
                user_id=request.user_id,
                topic=request.topic,
                theme=request.theme,
                blog_content=None,
                themed_blog=None,
                twitter_thread=None,
                hashnode_post=None,
                twitter_post=None,
                publish_schedule={
                    "twitter": request.schedule_twitter,
                    "hashnode": request.schedule_hashnode
                },
                workflow_status="initialized",
                current_node="start",
                human_input=None,
                hashnode_approval=None,
                twitter_approval=None
            )
            
            # Configure the workflow
            config: RunnableConfig = {
                "configurable": {
                    "thread_id": thread_id,
                    "recursion_limit": 50  # Increase recursion limit
                }
            }
            
            # Start the workflow
            result = workflow.invoke(initial_state, config)
            
            return {
                "thread_id": thread_id,
                "status": result.get("workflow_status", "started"),
                "current_node": result.get("current_node", "start"),
                "message": "Workflow started successfully",
                "requires_human_input": self._requires_human_input(result.get("current_node", "")),
                "result": result
            }
    
    async def provide_human_input(self, request: HumanInputRequest) -> Dict[str, Any]:
        """Provide human input to continue workflow"""
        with MongoDBSaver.from_conn_string(self.mongo_uri) as checkpointer:
            workflow = compile_workflow_with_checkpointer(checkpointer)

            # Get current state
            config: RunnableConfig = {
                "configurable": {
                    "thread_id": request.thread_id
                },
                "recursion_limit": 50
            }

            # Get current state to determine which approval to set
            current_state = checkpointer.get(config)
            current_node = ""
            if current_state:
                channel_values = current_state.get("channel_values", {})
                current_node = channel_values.get("current_node", "")

            # Determine which approval field to set based on current node
            if current_node == "hashnode_post":
                update_state = {"hashnode_approval": request.user_input, "human_input": request.user_input}
            elif current_node == "twitter_post":
                update_state = {"twitter_approval": request.user_input, "human_input": request.user_input}
            else:
                update_state = {"human_input": request.user_input}
            
            # Continue workflow
            result = workflow.invoke(update_state, config)
            
            return {
                "thread_id": request.thread_id,
                "status": result.get("workflow_status", "continued"),
                "current_node": result.get("current_node", ""),
                "message": f"Workflow continued with input: {request.user_input}",
                "requires_human_input": self._requires_human_input(result.get("current_node", "")),
                "result": result
            }
    
    async def get_workflow_status(self, thread_id: str) -> Dict[str, Any]:
        """Get current workflow status"""
        with MongoDBSaver.from_conn_string(self.mongo_uri) as checkpointer:
            # Get current state from checkpointer
            config: RunnableConfig = {
                "configurable": {
                    "thread_id": thread_id
                },
                "recursion_limit": 50
            }
            
            try:
                state = checkpointer.get(config)
                if state:
                    # Extract values from the nested state structure
                    channel_values = state.get("channel_values", {})
                    workflow_status = channel_values.get("workflow_status", "unknown")
                    current_node = channel_values.get("current_node", "")

                    return {
                        "thread_id": thread_id,
                        "status": workflow_status,
                        "current_node": current_node,
                        "requires_human_input": self._requires_human_input(current_node),
                        "state": state
                    }
                else:
                    return {
                        "thread_id": thread_id,
                        "status": "not_found",
                        "message": "Workflow not found"
                    }
            except Exception as e:
                return {
                    "thread_id": thread_id,
                    "status": "error",
                    "message": str(e)
                }
    
    def _requires_human_input(self, current_node: str) -> bool:
        """Check if current node requires human input"""
        return current_node in ["hashnode_post", "twitter_post"]