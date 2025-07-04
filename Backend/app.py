from typing import Dict, List, Optional, Literal, Any, Annotated
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import os
import tweepy
from hashnode_py.client import HashnodeClient
import pymongo
from pymongo import MongoClient
import json
import uuid
import requests
from contextlib import asynccontextmanager
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import interrupt, Command
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

load_dotenv()
client = OpenAI()
app = FastAPI(title="Blog Workflow API")

# State Models
class WorkflowState(BaseModel):
    blog_topic: Optional[str] = None
    theme_reference: Optional[str] = None
    blog_content: Optional[str] = None
    tweet_thread: Optional[List[str]] = None
    publish_date: Optional[datetime] = None
    status: str 
    thread_id: str
    post_id: Optional[str] = None
    messages: Annotated[list, add_messages]

# Node Input Models
class BlogNode(BaseModel):
    topic: str
    thread_id: str

class ThemeNode(BaseModel):
    reference_type: Literal["series", "anime", "game"]
    reference_name: str
    thread_id: str

class PublishNode(BaseModel):
    schedule_time: Optional[datetime] = None
    thread_id: str

class TweetNode(BaseModel):
    generate_thread: bool = True
    thread_id: str

#  Initialize MongoDB checkpoint
def get_checkpointer():
    DB_URI = os.getenv("MONGODB_URI", "mongodb://admin:admin@localhost:27017")
    return MongoDBSaver.from_conn_string(DB_URI)

#  Node Processing Functions
def process_blog_node(state: WorkflowState) -> WorkflowState:
    topic = state.blog_topic or "default_topic"
    prompt = f"write a blog post about {topic}"

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a professional blog writer."},
            {"role": "user", "content": prompt}
        ]
    )

    state.blog_content = response.choices[0].message.content
    state.status = "blog_created"
    return state

def process_theme_node(state: WorkflowState) -> WorkflowState:
    if not state.blog_content:
        raise HTTPException(status_code=400, detail="Blog content must be generated first")

    theme_reference = state.theme_reference or "default_theme"
    prompt = f"Rewrite the following blog post in the style of {theme_reference} '{theme_reference}':\n{state.blog_content}"
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": f"You are a creative writer who specializes in {theme_reference} style writing."},
            {"role": "user", "content": prompt}
        ]
    )

    state.blog_topic = response.choices[0].message.content
    state.status = "theme_applied"
    return state

def process_publish_node(state: WorkflowState) -> WorkflowState:
    if not state.blog_content:
        raise HTTPException(status_code=400, detail="Blog content must be generated first")

    # Initialize Hashnode API
    hashnode_api_key = os.getenv("HASHNODE_API_KEY")
    if not hashnode_api_key:
        raise HTTPException(status_code=500, detail="Hashnode API key not found")
    
    # Hashnode GraphQL endpoint
    url = "https://api.hashnode.com/"
    
    # GraphQL mutation for creating a post
    mutation = """
    mutation CreatePublicationStory($input: CreateStoryInput!) {
        createPublicationStory(input: $input) {
            post {
                _id
                title
                slug
                url
            }
        }
    }
    """
    
    # Prepare the input data
    variables = {
        "input": {
            "title": state.blog_topic,
            "contentMarkdown": state.blog_content,
            "tags": [],
            "isRepublished": False,
            "publishToPublication": True,
            "isDraft": True if state.publish_date else False
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": hashnode_api_key
    }
    
    try:
        response = requests.post(
            url,
            json={"query": mutation, "variables": variables},
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if "errors" in result:
                raise HTTPException(status_code=500, detail=f"Hashnode API error: {result['errors']}")
            
            post_data = result["data"]["createPublicationStory"]["post"]
            state.publish_date = state.publish_date
            state.status = "published"
            state.post_id = post_data["_id"]
        else:
            raise HTTPException(status_code=500, detail=f"Hashnode API request failed: {response.text}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish to Hashnode: {str(e)}")
    
    return state

def process_tweet_node(state: WorkflowState) -> WorkflowState:
    if not state.blog_content:
        raise HTTPException(status_code=400, detail="Blog content must be generated first")
    
    prompt = f"Convert this blog post into a Twitter thread (max 10 tweets):\n{state.blog_content}"

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Create an engaging Twitter thread from the given blog post."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content
    if not content:
        raise HTTPException(status_code=500, detail="Failed to generate tweet content")
    
    thread = content.split('\n')
    
    # Uncomment to enable Twitter posting
    # auth = tweepy.OAuthHandler(os.getenv("TWITTER_API_KEY"), os.getenv("TWITTER_API_SECRET"))
    # auth.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_TOKEN_SECRET"))
    # twitter_api = tweepy.API(auth)
    
    # previous_tweet_id = None
    # for tweet in thread:
    #     status = twitter_api.update_status(status=tweet, in_reply_to_status_id=previous_tweet_id)
    #     previous_tweet_id = status.id
    
    state.tweet_thread = thread
    return state

#  Create the workflow graph
def create_workflow_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("blog", process_blog_node)
    graph.add_node("theme", process_theme_node)
    graph.add_node("publish", process_publish_node)
    graph.add_node("tweet", process_tweet_node)

    graph.add_edge(START, "blog")
    graph.add_edge("blog", "theme")
    graph.add_edge("theme", "publish")
    graph.add_edge("publish", "tweet")
    graph.add_edge("tweet", END)

    return graph.compile()

# API Endpoints
@app.post("/workflow/start", response_model=Dict)
async def start_workflow(blog_input: BlogNode):
    """Start a new workflow with checkpointing"""
    try:
        checkpointer = get_checkpointer()
        graph = create_workflow_graph()
        
        # Initialize state
        initial_state = WorkflowState(
            blog_topic=blog_input.topic,
            theme_reference=None,
            blog_content=None,
            tweet_thread=None,
            publish_date=None,
            status="pending",
            thread_id=blog_input.thread_id,
            messages=[]
        )
        
        # Run the workflow
        result = graph.invoke(initial_state, checkpointer=checkpointer)
        
        return {
            "thread_id": blog_input.thread_id,
            "status": "workflow_started",
            "current_state": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

@app.post("/workflow/continue", response_model=Dict)
async def continue_workflow(thread_id: str):
    """Continue an existing workflow from its current state"""
    try:
        checkpointer = get_checkpointer()
        graph = create_workflow_graph()
        
        config = {"configurable": {"thread_id": thread_id}}

        # Get current state
        current_state = graph.get_state(config=config)
        if not current_state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        if not current_state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Continue from current state
        result = graph.invoke(current_state, checkpointer=checkpointer)
        
        return {
            "thread_id": thread_id,
            "status": "workflow_continued",
            "current_state": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to continue workflow: {str(e)}")

@app.get("/workflow/status/{thread_id}", response_model=Dict)
async def get_workflow_status(thread_id: str):
    """Get the current status of a workflow"""
    try:
        checkpointer = get_checkpointer()
        graph = create_workflow_graph()
        
        config = {"configurable": {"thread_id": thread_id}}
        current_state = graph.get_state(config, checkpointer=checkpointer)
        
        if not current_state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "thread_id": thread_id,
            "status": current_state.get("status", "unknown"),
            "current_state": current_state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

@app.post("/workflow/apply-theme", response_model=Dict)
async def apply_theme_to_workflow(theme_input: ThemeNode):
    """Apply theme to an existing workflow"""
    try:
        checkpointer = get_checkpointer()
        graph = create_workflow_graph()
        
        config = {"configurable": {"thread_id": theme_input.thread_id}}
        current_state = graph.get_state(config, checkpointer=checkpointer)
        
        if not current_state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Update state with theme
        updated_state = process_theme_node(current_state, theme_input)
        
        # Save updated state
        graph.invoke(updated_state, config, checkpointer=checkpointer)
        
        return {
            "thread_id": theme_input.thread_id,
            "status": "theme_applied",
            "current_state": updated_state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply theme: {str(e)}")

@app.post("/workflow/publish", response_model=Dict)
async def publish_workflow(publish_input: PublishNode):
    """Publish an existing workflow"""
    try:
        checkpointer = get_checkpointer()
        graph = create_workflow_graph()
        
        config = {"configurable": {"thread_id": publish_input.thread_id}}
        current_state = graph.get_state(config, checkpointer=checkpointer)
        
        if not current_state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Update state with publish
        updated_state = process_publish_node(current_state, publish_input)
        
        # Save updated state
        graph.invoke(updated_state, config, checkpointer=checkpointer)
        
        return {
            "thread_id": publish_input.thread_id,
            "status": "published",
            "current_state": updated_state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish: {str(e)}")

@app.post("/workflow/generate-tweets", response_model=Dict)
async def generate_tweets_for_workflow(tweet_input: TweetNode):
    """Generate tweets for an existing workflow"""
    try:
        checkpointer = get_checkpointer()
        graph = create_workflow_graph()
        
        config = {"configurable": {"thread_id": tweet_input.thread_id}}
        current_state = graph.get_state(config, checkpointer=checkpointer)
        
        if not current_state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Update state with tweets
        updated_state = process_tweet_node(current_state, tweet_input)
        
        # Save updated state
        graph.invoke(updated_state, config, checkpointer=checkpointer)
        
        return {
            "thread_id": tweet_input.thread_id,
            "status": "tweets_generated",
            "current_state": updated_state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate tweets: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)