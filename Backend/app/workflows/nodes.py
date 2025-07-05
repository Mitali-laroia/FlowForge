from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..core.config import settings
from pydantic import SecretStr
import os
from datetime import datetime
from ..schemas.workflow_state import WorkflowState

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",  # Using gpt-4o-mini as gpt-4.1 doesn't exist
    temperature=0.7,
    api_key=SecretStr(settings.OPENAI_API_KEY)
)

def start_node(state: WorkflowState) -> Dict[str, Any]:
    """Start node - initializes the workflow with user_id"""
    print(f"Starting workflow for user: {state['user_id']}")
    return {
        "workflow_status": "started",
        "current_node": "generate_blog",
        "messages": state["messages"] + [{"role": "system", "content": f"Workflow started for user {state['user_id']}"}]
    }

def generate_blog_node(state: WorkflowState) -> Dict[str, Any]:
    """Generate blog content based on topic"""
    topic = state.get("topic", "")
    
    prompt = f"""
    Write a comprehensive blog post about: {topic}
    
    Requirements:
    - Minimum 800 words
    - Engaging and informative
    - Include introduction, main points, and conclusion
    - Use clear, professional language
    - Include relevant examples or case studies
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    blog_content = response.content
    
    return {
        "blog_content": blog_content,
        "current_node": "apply_theme",
        "workflow_status": "blog_generated",
        "messages": state["messages"] + [{"role": "assistant", "content": f"Blog generated: {blog_content[:100]}..."}]
    }

def apply_theme_node(state: WorkflowState) -> Dict[str, Any]:
    """Apply theme to the blog content"""
    blog_content = state.get("blog_content", "")
    theme = state.get("theme", "")
    
    if not theme:
        # If no theme provided, skip this step
        return {
            "themed_blog": blog_content,
            "current_node": "twitter_thread",
            "workflow_status": "theme_applied",
            "messages": state["messages"] + [{"role": "assistant", "content": "No theme applied, proceeding to Twitter thread generation"}]
        }
    
    prompt = f"""
    Rewrite the following blog content to revolve around the theme: {theme}
    
    Original blog:
    {blog_content}
    
    Requirements:
    - Maintain the same structure and key points
    - Incorporate the theme naturally throughout the content
    - Keep the same length and quality
    - Make it engaging for fans of {theme}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    themed_blog = response.content
    
    return {
        "themed_blog": themed_blog,
        "current_node": "twitter_thread",
        "workflow_status": "theme_applied",
        "messages": state["messages"] + [{"role": "assistant", "content": f"Theme applied: {themed_blog[:100]}..."}]
    }

def twitter_thread_node(state: WorkflowState) -> Dict[str, Any]:
    """Generate Twitter thread content"""
    blog_content = state.get("themed_blog") or state.get("blog_content", "")
    
    prompt = f"""
    Create an engaging Twitter thread (5-8 tweets) to promote this blog post:
    
    Blog content:
    {blog_content}
    
    Requirements:
    - 5-8 tweets maximum
    - Each tweet under 280 characters
    - Engaging and shareable
    - Include relevant hashtags
    - End with a call-to-action
    - Number each tweet (1/5, 2/5, etc.)
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    twitter_thread = response.content
    
    return {
        "twitter_thread": twitter_thread,
        "current_node": "hashnode_post",
        "workflow_status": "twitter_thread_created",
        "messages": state["messages"] + [{"role": "assistant", "content": f"Twitter thread created: {twitter_thread[:100]}..."}]
    }

def hashnode_post_node(state: WorkflowState) -> Dict[str, Any]:
    """Prepare Hashnode post data"""
    blog_content = state.get("themed_blog") or state.get("blog_content", "")
    topic = state.get("topic", "")
    
    # Extract title from first few lines
    if blog_content is None:
        raise ValueError("Blog content is None")
    lines = blog_content.split('\n')
    title = lines[0].replace('#', '').strip() if lines else f"Blog about {topic}"
    
    hashnode_post = {
        "title": title,
        "content": blog_content,
        "tags": [topic.lower().replace(' ', '-')] if topic else ["blog"],
        "subdomain": "your-subdomain"
    }
    
    return {
        "hashnode_post": hashnode_post,
        "current_node": "human_approval_hashnode",
        "workflow_status": "hashnode_ready",
        "messages": state["messages"] + [{"role": "assistant", "content": f"Hashnode post prepared: {title}"}]
    }

def twitter_post_node(state: WorkflowState) -> Dict[str, Any]:
    """Prepare Twitter post data"""
    twitter_thread = state.get("twitter_thread", "")
    
    twitter_post = {
        "content": twitter_thread,
        "scheduled_time": None  # Will be set by human input
    }
    
    return {
        "twitter_post": twitter_post,
        "current_node": "human_approval_twitter",
        "workflow_status": "twitter_ready",
        "messages": state["messages"] + [{"role": "assistant", "content": "Twitter post prepared for approval"}]
    }

def human_approval_hashnode_node(state: WorkflowState) -> Dict[str, Any]:
    """Wait for human approval for Hashnode publishing"""
    return {
        "current_node": "human_approval_hashnode",
        "workflow_status": "waiting_hashnode_approval",
        "messages": state["messages"] + [{"role": "system", "content": "Waiting for human approval to publish on Hashnode"}]
    }

def human_approval_twitter_node(state: WorkflowState) -> Dict[str, Any]:
    """Wait for human approval for Twitter publishing"""
    return {
        "current_node": "human_approval_twitter",
        "workflow_status": "waiting_twitter_approval",
        "messages": state["messages"] + [{"role": "system", "content": "Waiting for human approval to publish on Twitter"}]
    }

def publish_hashnode_node(state: WorkflowState) -> Dict[str, Any]:
    """Publish to Hashnode"""
    hashnode_post = state.get("hashnode_post", {})
    
    # Ensure hashnode_post is a dictionary
    if not isinstance(hashnode_post, dict):
        hashnode_post = {}
    
    # Simulate API call
    published_post = {
        **hashnode_post,
        "published_at": datetime.now().isoformat(),
        "url": f"https://your-subdomain.hashnode.dev/{hashnode_post.get('title', 'blog').lower().replace(' ', '-')}"
    }
    
    return {
        "hashnode_post": published_post,
        "current_node": "publish_twitter",
        "workflow_status": "hashnode_published",
        "messages": state["messages"] + [{"role": "assistant", "content": f"Published on Hashnode: {published_post['url']}"}]
    }

def publish_twitter_node(state: WorkflowState) -> Dict[str, Any]:
    """Publish to Twitter"""
    # This would integrate with Twitter API
    # For now, we'll simulate the publishing
    twitter_post = state.get("twitter_post", {})

    if not isinstance(twitter_post, dict):
        twitter_post = {}
    
    # Simulate API call
    published_tweet = {
        **twitter_post,
        "published_at": datetime.now().isoformat(),
        "tweet_id": "1234567890"
    }
    
    return {
        "twitter_post": published_tweet,
        "current_node": "end",
        "workflow_status": "completed",
        "messages": state["messages"] + [{"role": "assistant", "content": "Published on Twitter successfully"}]
    } 