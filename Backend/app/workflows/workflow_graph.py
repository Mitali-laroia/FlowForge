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
    
    # Add nodes (REMOVE the human approval nodes)
    workflow.add_node("start", start_node)
    workflow.add_node("generate_blog", generate_blog_node)
    workflow.add_node("apply_theme", apply_theme_node)
    workflow.add_node("twitter_thread", twitter_thread_node)
    workflow.add_node("hashnode_post", hashnode_post_node)
    workflow.add_node("twitter_post", twitter_post_node)
    workflow.add_node("publish_hashnode", publish_hashnode_node)
    workflow.add_node("publish_twitter", publish_twitter_node)
    
    # Define conditional edges
    def should_continue_to_theme(state: Dict[str, Any]) -> str:
        """Decide whether to apply theme or skip to Twitter thread"""
        theme = state.get("theme")
        return "apply_theme" if theme else "twitter_thread"
    
    def should_publish_hashnode(state: Dict[str, Any]) -> str:
        """Decide whether to publish on Hashnode based on human input"""
        hashnode_approval = state.get("hashnode_approval")

        if hashnode_approval is None:
            # PAUSE the workflow here - don't route anywhere
            return END  # End the workflow until human input is provided

        hashnode_approval = str(hashnode_approval).lower()
        if hashnode_approval in ["yes", "approve"]:
            return "publish_hashnode"
        elif hashnode_approval in ["no", "reject"]:
            return "twitter_post"
        else:
            return END  # End the workflow for invalid input
    
    def should_publish_twitter(state: Dict[str, Any]) -> str:
        """Decide whether to publish on Twitter based on human input"""
        twitter_approval = state.get("twitter_approval")

        if twitter_approval is None:
            # PAUSE the workflow here - don't route anywhere
            return END  # End the workflow until human input is provided

        twitter_approval = str(twitter_approval).lower()
        if twitter_approval in ["yes", "approve"]:
            return "publish_twitter"
        elif twitter_approval in ["no", "reject"]:
            return END
        else:
            return END  # End the workflow for invalid input
    
    # Add edges - LINEAR FLOW with pauses
    workflow.add_edge(START, "start")
    workflow.add_edge("start", "generate_blog")
    workflow.add_conditional_edges("generate_blog", should_continue_to_theme)
    workflow.add_edge("apply_theme", "twitter_thread")
    workflow.add_edge("twitter_thread", "hashnode_post")
    workflow.add_conditional_edges("hashnode_post", should_publish_hashnode)
    workflow.add_edge("publish_hashnode", "twitter_post")
    workflow.add_conditional_edges("twitter_post", should_publish_twitter)
    workflow.add_edge("publish_twitter", END)
    
    return workflow

def compile_workflow_with_checkpointer(checkpointer):
    """Compile the workflow with MongoDB checkpointer"""
    workflow = create_workflow_graph()
    return workflow.compile(checkpointer=checkpointer) 