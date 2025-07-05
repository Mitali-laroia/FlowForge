from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.graph.message import add_messages
from typing import Dict, Any
from .nodes import *
from ..schemas.workflow_state import WorkflowState

def create_workflow_graph():
    """Create the N8N workflow graph"""
    
    # Create the state graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("start", start_node)
    workflow.add_node("generate_blog", generate_blog_node)
    workflow.add_node("apply_theme", apply_theme_node)
    workflow.add_node("twitter_thread", twitter_thread_node)
    workflow.add_node("hashnode_post", hashnode_post_node)
    workflow.add_node("twitter_post", twitter_post_node)
    workflow.add_node("human_approval_hashnode", human_approval_hashnode_node)
    workflow.add_node("human_approval_twitter", human_approval_twitter_node)
    workflow.add_node("publish_hashnode", publish_hashnode_node)
    workflow.add_node("publish_twitter", publish_twitter_node)
    
    # Define conditional edges
    def should_continue_to_theme(state: Dict[str, Any]) -> str:
        """Decide whether to apply theme or skip to Twitter thread"""
        return "apply_theme" if state.get("theme") else "twitter_thread"
    
    def should_publish_hashnode(state: Dict[str, Any]) -> str:
        """Decide whether to publish on Hashnode based on human input"""
        human_input = state.get("human_input", "").lower()
        if human_input == "yes" or human_input == "approve":
            return "publish_hashnode"
        elif human_input == "no" or human_input == "reject":
            return "publish_twitter"  # Skip to Twitter
        else:
            return "human_approval_hashnode"  # Wait for input
    
    def should_publish_twitter(state: Dict[str, Any]) -> str:
        """Decide whether to publish on Twitter based on human input"""
        human_input = state.get("human_input", "").lower()
        if human_input == "yes" or human_input == "approve":
            return "publish_twitter"
        elif human_input == "no" or human_input == "reject":
            return "end"  # End workflow
        else:
            return "human_approval_twitter"  # Wait for input
    
    # Add edges
    workflow.add_edge(START, "start")
    workflow.add_edge("start", "generate_blog")
    workflow.add_conditional_edges("generate_blog", should_continue_to_theme)
    workflow.add_edge("apply_theme", "twitter_thread")
    workflow.add_edge("twitter_thread", "hashnode_post")
    workflow.add_edge("hashnode_post", "human_approval_hashnode")
    workflow.add_conditional_edges("human_approval_hashnode", should_publish_hashnode)
    workflow.add_edge("publish_hashnode", "twitter_post")
    workflow.add_edge("twitter_post", "human_approval_twitter")
    workflow.add_conditional_edges("human_approval_twitter", should_publish_twitter)
    workflow.add_edge("publish_twitter", END)
    
    return workflow

def compile_workflow_with_checkpointer(checkpointer):
    """Compile the workflow with MongoDB checkpointer"""
    workflow = create_workflow_graph()
    return workflow.compile(checkpointer=checkpointer) 