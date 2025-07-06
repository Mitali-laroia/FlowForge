from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr
from ..core.config import settings
from ..services.hashnode_service import HashnodeService
from ..schemas.workflow_state import WorkflowState
from datetime import datetime

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=SecretStr(settings.OPENAI_API_KEY)
)

# Initialize Hashnode service
hashnode_service = HashnodeService()

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
        "current_node": "apply_theme",  # This will be overridden by conditional edge
        "workflow_status": "blog_generated",
        "messages": state["messages"] + [{"role": "assistant", "content": f"Blog generated: {blog_content[:100]}..."}]
    }

def apply_theme_node(state: WorkflowState) -> Dict[str, Any]:
    """Apply theme to the blog content"""
    blog_content = state.get("blog_content", "")
    theme = state.get("theme")
    
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
    """Prepare Hashnode post data and pause for human approval"""
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
        "current_node": "hashnode_post",  # Stay at this node
        "workflow_status": "waiting_hashnode_approval",  # Indicate waiting
        "messages": state["messages"] + [{"role": "assistant", "content": f"Hashnode post prepared: {title}. Waiting for approval."}]
    }

def twitter_post_node(state: WorkflowState) -> Dict[str, Any]:
    """Prepare Twitter post data and pause for human approval"""
    twitter_thread = state.get("twitter_thread", "")
    
    twitter_post = {
        "content": twitter_thread,
        "scheduled_time": None
    }
    
    return {
        "twitter_post": twitter_post,
        "current_node": "twitter_post",  # Stay at this node
        "workflow_status": "waiting_twitter_approval",  # Indicate waiting
        "messages": state["messages"] + [{"role": "assistant", "content": "Twitter post prepared. Waiting for approval."}]
    }

def publish_hashnode_node(state: WorkflowState) -> Dict[str, Any]:
    """Publish to Hashnode using real API"""
    hashnode_post = state.get("hashnode_post", {})
    
    if not isinstance(hashnode_post, dict):
        raise ValueError("Hashnode post data is invalid")
    
    try:
        # Extract post data
        title = hashnode_post.get("title", "Untitled Post")
        content = hashnode_post.get("content", "")
        tags = hashnode_post.get("tags", ["blog"])
        
        # Ensure content is not empty
        if not content:
            raise ValueError("Blog content is empty")
        
        # Create tags list (ensure they're strings and not too long)
        processed_tags = []
        for tag in tags:
            if isinstance(tag, str) and len(tag) <= 20:
                processed_tags.append(tag)
        
        # Add default tag if none provided
        if not processed_tags:
            processed_tags = ["blog"]
        
        # First create a draft
        print(f"Creating draft for title: {title}")
        draft_result = hashnode_service.create_post(
            title=title,
            content=content,
            tags=processed_tags
        )

        print(f"Draft creation result: {draft_result}")

        if not draft_result.get("success"):
            raise Exception(f"Failed to create draft: {draft_result.get('message', 'Unknown error')}")

        draft_id = draft_result.get("draft_id")
        print(f"Draft ID received: {draft_id}")

        if not draft_id:
            raise Exception("Draft ID not returned from Hashnode")

        # Then publish the draft
        print(f"Publishing draft with ID: {draft_id}")
        publish_result = hashnode_service.publish_draft(draft_id)
        print(f"Publish result: {publish_result}")
        
        if not publish_result.get("success"):
            raise Exception(f"Failed to publish draft: {publish_result.get('message', 'Unknown error')}")
        
        # Update the hashnode_post with real data
        published_post = {
            **hashnode_post,
            "published_at": datetime.now().isoformat(),
            "hashnode_id": publish_result.get("post", {}).get("id"),
            "url": publish_result.get("post", {}).get("url"),
            "slug": publish_result.get("post", {}).get("slug"),
            "success": publish_result.get("success", False),
            "message": publish_result.get("message", "Post published successfully"),
            "draft_id": draft_id
        }
        
        return {
            "hashnode_post": published_post,
            "current_node": "twitter_post",
            "workflow_status": "hashnode_published",
            "messages": state["messages"] + [
                {
                    "role": "assistant", 
                    "content": f"Published on Hashnode: {published_post.get('url', 'URL not available')}"
                }
            ]
        }
        
    except Exception as e:
        # Log the error and return error state
        error_message = f"Failed to publish on Hashnode: {str(e)}"
        print(error_message)
        
        return {
            "hashnode_post": {
                **hashnode_post,
                "error": error_message,
                "published_at": datetime.now().isoformat(),
                "success": False
            },
            "current_node": "twitter_post",  # Continue to next step even if failed
            "workflow_status": "hashnode_failed",
            "messages": state["messages"] + [
                {
                    "role": "system", 
                    "content": error_message
                }
            ]
        }

def publish_twitter_node(state: WorkflowState) -> Dict[str, Any]:
    """Publish to Twitter"""
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