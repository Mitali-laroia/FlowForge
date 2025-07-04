from typing import Dict, List, Optional, Literal, Any, Annotated
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import os
import tweepy
import requests
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.graph.message import add_messages
from langchain_core.runnables import RunnableConfig
from typing_extensions import TypedDict
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize OpenAI client
client = OpenAI()
app = FastAPI(title="Blog Workflow API")

# FIXED: Proper TypedDict state structure following checkpointer.py pattern
class BlogWorkflowState(TypedDict):
    blog_topic: Optional[str]
    theme_reference: Optional[str]
    theme_type: Optional[str]
    blog_content: Optional[str]
    tweet_thread: Optional[List[str]]
    publish_date: Optional[str]
    status: str
    thread_id: str
    post_id: Optional[str]
    messages: Annotated[List[dict], add_messages]
    error: Optional[str]
    current_node: Optional[str]

# Pydantic models for API requests only
class StartWorkflowRequest(BaseModel):
    topic: str
    thread_id: Optional[str] = None

class ApplyThemeRequest(BaseModel):
    thread_id: str
    theme_type: Literal["series", "anime", "game", "movie", "book"]
    theme_name: str

class PublishRequest(BaseModel):
    thread_id: str
    schedule_time: Optional[datetime] = None

class GenerateTweetsRequest(BaseModel):
    thread_id: str

class ContinueWorkflowRequest(BaseModel):
    thread_id: str
    next_node: Optional[str] = None

# FIXED: Following checkpointer.py pattern for MongoDB connection
def get_checkpointer():
    """Get MongoDB checkpointer instance"""
    DB_URI = os.getenv("MONGODB_URI", "mongodb://admin:admin@mongodb:27017")
    try:
        checkpointer = MongoDBSaver.from_conn_string(DB_URI)
        logger.info("MongoDB checkpointer initialized successfully")
        return checkpointer
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB checkpointer: {e}")
        raise

# FIXED: Node functions that properly handle state
def blog_generation_node(state: BlogWorkflowState) -> BlogWorkflowState:
    """Generate blog content based on topic"""
    logger.info(f"Generating blog for topic: {state.get('blog_topic')}")
    
    try:
        topic = state.get("blog_topic")
        if not topic:
            raise ValueError("Blog topic is required")
            
        prompt = f"""Write a comprehensive blog post about: {topic}
        
        Please include:
        - An engaging title (start with # for markdown)
        - Introduction
        - Main content with clear sections
        - Conclusion
        - Format it in markdown
        
        Make it informative and engaging, around 800-1200 words.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional blog writer who creates engaging, well-structured content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Failed to generate blog content")

        # Return updated state
        return {
            **state,
            "blog_content": content,
            "status": "blog_generated",
            "current_node": "blog_generation",
            "messages": [
                *state.get("messages", []),
                {
                    "role": "assistant",
                    "content": f"Blog generated successfully for topic: {topic}",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in blog generation: {str(e)}")
        return {
            **state,
            "error": f"Blog generation failed: {str(e)}",
            "status": "error",
            "current_node": "blog_generation"
        }

def theme_application_node(state: BlogWorkflowState) -> BlogWorkflowState:
    """Apply theme styling to the blog content"""
    logger.info(f"Applying theme: {state.get('theme_reference')}")
    
    try:
        if not state.get("blog_content"):
            raise ValueError("Blog content must be generated first")
            
        theme_ref = state.get("theme_reference")
        theme_type = state.get("theme_type", "series")
        
        if not theme_ref:
            # Skip theme application if no theme specified
            return {
                **state,
                "status": "theme_skipped",
                "current_node": "theme_application"
            }
            
        prompt = f"""Rewrite the following blog post in the style and tone of the {theme_type} '{theme_ref}'.
        
        Instructions:
        - Maintain the core information and structure
        - Adapt the writing style, tone, and examples to match the {theme_type}
        - Keep it engaging and authentic to the {theme_type}'s style
        - Preserve the markdown formatting
        - Keep the same length and depth
        
        Original blog post:
        {state['blog_content']}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a creative writer who specializes in adapting content to match the style of various {theme_type}s."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.8
        )

        themed_content = response.choices[0].message.content
        if not themed_content:
            raise ValueError("Failed to apply theme")

        return {
            **state,
            "blog_content": themed_content,
            "status": "theme_applied",
            "current_node": "theme_application",
            "messages": [
                *state.get("messages", []),
                {
                    "role": "assistant",
                    "content": f"Theme '{theme_ref}' applied successfully",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in theme application: {str(e)}")
        return {
            **state,
            "error": f"Theme application failed: {str(e)}",
            "status": "error",
            "current_node": "theme_application"
        }

def publish_node(state: BlogWorkflowState) -> BlogWorkflowState:
    """Publish blog to Hashnode"""
    logger.info(f"Publishing blog to Hashnode for thread: {state.get('thread_id')}")
    
    try:
        if not state.get("blog_content"):
            raise ValueError("Blog content must be generated first")
            
        # Extract title from blog content
        if state["blog_content"] is None:
            raise ValueError("Blog content is required")

        content_lines = state["blog_content"].split('\n')
        title = state.get("blog_topic", "Generated Blog Post")
        
        # Find title in markdown format
        for line in content_lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
                
        hashnode_api_key = os.getenv("HASHNODE_API_KEY")
        if not hashnode_api_key:
            raise ValueError("Hashnode API key not configured")
            
        url = "https://gql.hashnode.com/"
        
        mutation = """
        mutation PublishPost($input: PublishPostInput!) {
            publishPost(input: $input) {
                post {
                    id
                    title
                    slug
                    url
                }
            }
        }
        """
        
        publication_id = os.getenv("HASHNODE_PUBLICATION_ID")
        if not publication_id:
            raise ValueError("Hashnode publication ID not configured")
            
        variables = {
            "input": {
                "title": title,
                "contentMarkdown": state["blog_content"],
                "publicationId": publication_id,
                "tags": [],
                "publishedAt": state.get("publish_date"),
                "isDraft": False
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {hashnode_api_key}"
        }
        
        response = requests.post(
            url,
            json={"query": mutation, "variables": variables},
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            raise ValueError(f"Hashnode API request failed: {response.text}")
            
        result = response.json()
        if "errors" in result:
            raise ValueError(f"Hashnode API error: {result['errors']}")
            
        post_data = result["data"]["publishPost"]["post"]
        
        return {
            **state,
            "post_id": post_data["id"],
            "status": "published",
            "current_node": "publish",
            "messages": [
                *state.get("messages", []),
                {
                    "role": "assistant",
                    "content": f"Blog published successfully: {post_data['url']}",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in publishing: {str(e)}")
        return {
            **state,
            "error": f"Publishing failed: {str(e)}",
            "status": "error",
            "current_node": "publish"
        }

def tweet_generation_node(state: BlogWorkflowState) -> BlogWorkflowState:
    """Generate Twitter thread from blog content"""
    logger.info(f"Generating Twitter thread for thread: {state.get('thread_id')}")
    
    try:
        if not state.get("blog_content"):
            raise ValueError("Blog content must be generated first")
            
        # Get first 1500 characters for context
        if state["blog_content"] is None:
            raise ValueError("Blog content is required")

        blog_excerpt = state["blog_content"][:1500]
        
        prompt = f"""Convert the following blog post into an engaging Twitter thread.
        
        Instructions:
        - Create 5-8 tweets maximum
        - Each tweet should be under 280 characters
        - Start with a hook tweet
        - Include key points from the blog
        - End with a call to action
        - Number each tweet (1/n, 2/n, etc.)
        - Make it engaging and shareable
        - Each tweet should be on a new line
        
        Blog content excerpt:
        {blog_excerpt}...
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a social media expert who creates engaging Twitter threads."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.8
        )

        thread_content = response.choices[0].message.content
        if not thread_content:
            raise ValueError("Failed to generate Twitter thread")
            
        # Parse the thread into individual tweets
        tweets = []
        lines = thread_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('Tweet') or line.startswith('Thread'):
                continue
                
            if line.startswith(('1/', '2/', '3/', '4/', '5/', '6/', '7/', '8/')):
                parts = line.split(' ', 1)
                if len(parts) > 1:
                    line = parts[1]
                    
            if len(line) > 10 and len(line) <= 280:
                tweets.append(line)
        
        if not tweets:
            tweets = [f"Just wrote a blog post about {state.get('blog_topic', 'an interesting topic')}! 🧵 Thread below:"]
            
        return {
            **state,
            "tweet_thread": tweets,
            "status": "tweets_generated",
            "current_node": "tweet_generation",
            "messages": [
                *state.get("messages", []),
                {
                    "role": "assistant",
                    "content": f"Generated Twitter thread with {len(tweets)} tweets",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in tweet generation: {str(e)}")
        return {
            **state,
            "error": f"Tweet generation failed: {str(e)}",
            "status": "error",
            "current_node": "tweet_generation"
        }

# FIXED: Following checkpointer.py pattern for graph compilation
def compile_graph_with_checkpointer(checkpointer):
    """Compile graph with checkpointer following checkpointer.py pattern"""
    graph_builder = StateGraph(BlogWorkflowState)
    
    # Add nodes
    graph_builder.add_node("blog_generation", blog_generation_node)
    graph_builder.add_node("theme_application", theme_application_node)
    graph_builder.add_node("publish", publish_node)
    graph_builder.add_node("tweet_generation", tweet_generation_node)
    
    # Add edges - simple linear flow like in checkpointer.py
    graph_builder.add_edge(START, "blog_generation")
    graph_builder.add_edge("blog_generation", "theme_application")
    graph_builder.add_edge("theme_application", "publish")
    graph_builder.add_edge("publish", "tweet_generation")
    graph_builder.add_edge("tweet_generation", END)
    
    # Compile with checkpointer
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer

# Global workflow instance
_workflow = None

def get_workflow():
    """Get or create the workflow instance"""
    global _workflow
    if _workflow is None:
        checkpointer = get_checkpointer()
        _workflow = compile_graph_with_checkpointer(checkpointer)
        logger.info("Workflow compiled successfully")
    return _workflow

# FIXED: API endpoints with proper state handling
@app.post("/workflow/start")
async def start_workflow(request: StartWorkflowRequest):
    """Start a new blog workflow"""
    try:
        thread_id = request.thread_id or str(uuid.uuid4())
        workflow = get_workflow()
        
        # Create initial state following the TypedDict structure
        initial_state: BlogWorkflowState = {
            "blog_topic": request.topic,
            "theme_reference": None,
            "theme_type": None,
            "blog_content": None,
            "tweet_thread": None,
            "publish_date": None,
            "status": "started",
            "thread_id": thread_id,
            "post_id": None,
            "messages": [],
            "error": None,
            "current_node": None
        }
        
        # Configuration for checkpointing - following checkpointer.py pattern
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        
        # Execute the workflow
        result = workflow.invoke(initial_state, config)
        
        return {
            "thread_id": thread_id,
            "status": result.get("status"),
            "current_node": result.get("current_node"),
            "message": "Workflow started and blog generated",
            "has_blog_content": bool(result.get("blog_content")),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error starting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

@app.post("/workflow/apply-theme")
async def apply_theme(request: ApplyThemeRequest):
    """Apply theme to existing workflow"""
    try:
        workflow = get_workflow()
        config: RunnableConfig = {"configurable": {"thread_id": request.thread_id}}
        
        # Get current state
        current_state_snapshot = workflow.get_state(config)
        if not current_state_snapshot or not current_state_snapshot.values:
            raise HTTPException(status_code=404, detail="Workflow not found")
            
        # Update state with theme information - cast to BlogWorkflowState
        current_state = dict(current_state_snapshot.values)  # Convert to dict
        updated_state = {
            **current_state,
            "theme_reference": request.theme_name,
            "theme_type": request.theme_type
        }  # Remove explicit typing
        
        # Apply theme using the theme_application_node directly
        result = theme_application_node(updated_state)  # type: ignore
        
        # Update the state in the checkpointer
        workflow.update_state(config, result)
        
        return {
            "thread_id": request.thread_id,
            "status": result.get("status"),
            "current_node": result.get("current_node"),
            "message": "Theme applied successfully",
            "has_blog_content": bool(result.get("blog_content")),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error applying theme: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to apply theme: {str(e)}")

@app.post("/workflow/publish")
async def publish_blog(request: PublishRequest):
    """Publish blog to Hashnode"""
    try:
        workflow = get_workflow()
        config: RunnableConfig = {"configurable": {"thread_id": request.thread_id}}
        
        # Get current state
        current_state_snapshot = workflow.get_state(config)
        if not current_state_snapshot or not current_state_snapshot.values:
            raise HTTPException(status_code=404, detail="Workflow not found")
            
        # Update state with publish date if provided
        current_state = dict(current_state_snapshot.values)
        updated_state = {
            **current_state,
            "publish_date": request.schedule_time.isoformat() if request.schedule_time else None
        }
        
        # Publish using the publish_node directly
        result = publish_node(updated_state)  # type: ignore
        
        # Update the state in the checkpointer
        workflow.update_state(config, result)
        
        return {
            "thread_id": request.thread_id,
            "status": result.get("status"),
            "current_node": result.get("current_node"),
            "message": "Blog published successfully",
            "post_id": result.get("post_id"),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error publishing blog: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to publish blog: {str(e)}")

@app.post("/workflow/generate-tweets")
async def generate_tweets(request: GenerateTweetsRequest):
    """Generate Twitter thread for blog"""
    try:
        workflow = get_workflow()
        config: RunnableConfig = {"configurable": {"thread_id": request.thread_id}}
        
        # Get current state
        current_state_snapshot = workflow.get_state(config)
        if not current_state_snapshot or not current_state_snapshot.values:
            raise HTTPException(status_code=404, detail="Workflow not found")
            
        # Generate tweets using the tweet_generation_node directly
        result = tweet_generation_node(current_state_snapshot.values)  # type: ignore
        
        # Update the state in the checkpointer
        workflow.update_state(config, result)
        
        return {
            "thread_id": request.thread_id,
            "status": result.get("status"),
            "current_node": result.get("current_node"),
            "message": "Twitter thread generated successfully",
            "tweet_count": len(result.get("tweet_thread") or []),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error generating tweets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate tweets: {str(e)}")

@app.get("/workflow/status/{thread_id}")
async def get_workflow_status(thread_id: str):
    """Get current workflow status"""
    try:
        workflow = get_workflow()
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        current_state_snapshot = workflow.get_state(config)
        
        if not current_state_snapshot or not current_state_snapshot.values:
            raise HTTPException(status_code=404, detail="Workflow not found")
            
        state = current_state_snapshot.values
        
        return {
            "thread_id": thread_id,
            "status": state.get("status"),
            "current_node": state.get("current_node"),
            "blog_topic": state.get("blog_topic"),
            "theme_reference": state.get("theme_reference"),
            "has_blog_content": bool(state.get("blog_content")),
            "has_tweets": bool(state.get("tweet_thread")),
            "post_id": state.get("post_id"),
            "error": state.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

@app.get("/workflow/content/{thread_id}")
async def get_workflow_content(thread_id: str):
    """Get full workflow content"""
    try:
        workflow = get_workflow()
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        current_state_snapshot = workflow.get_state(config)
        
        if not current_state_snapshot or not current_state_snapshot.values:
            raise HTTPException(status_code=404, detail="Workflow not found")
            
        state = current_state_snapshot.values
        
        return {
            "thread_id": thread_id,
            "blog_topic": state.get("blog_topic"),
            "blog_content": state.get("blog_content"),
            "tweet_thread": state.get("tweet_thread"),
            "theme_reference": state.get("theme_reference"),
            "theme_type": state.get("theme_type"),
            "status": state.get("status"),
            "current_node": state.get("current_node"),
            "post_id": state.get("post_id"),
            "messages": state.get("messages", []),
            "error": state.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error getting workflow content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow content: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Blog Workflow API", 
        "version": "2.0.0",
        "endpoints": {
            "start": "POST /workflow/start",
            "apply_theme": "POST /workflow/apply-theme",
            "publish": "POST /workflow/publish",
            "generate_tweets": "POST /workflow/generate-tweets",
            "status": "GET /workflow/status/{thread_id}",
            "content": "GET /workflow/content/{thread_id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)