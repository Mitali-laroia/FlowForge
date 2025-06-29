from typing import Dict, List, Optional, Literal
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import os
import tweepy
from hashnode_py.client import HashnodeClient

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
    status: str = "pending"

# Node Input Models
class BlogNode(BaseModel):
    topic: str

class ThemeNode(BaseModel):
    reference_type: Literal["series", "anime", "game"]
    reference_name: str

class PublishNode(BaseModel):
    schedule_time: Optional[datetime] = None

class TweetNode(BaseModel):
    generate_thread: bool = True

#  Node Processing Functions
def process_blog_node(state: Dict, input_data: BlogNode) -> Dict:
    prompt = f"write a blog post about {input_data.topic}"

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a professional blog writer."},
            {"role": "user", "content": prompt}
        ]
    )

    state["blog_topic"] = input_data.topic
    state["blog_content"] = response.choices[0].message.content
    return state

def process_theme_node(state: Dict, input_data: ThemeNode) -> Dict:
    if not state.get("blog_content"):
        raise HTTPException(status_code=400, detail="Blog content must be generated first")

    prompt = f"Rewrite the following blog post in the style of {input_data.reference_type} '{input_data.reference_name}':\n{state['blog_content']}"
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": f"You are a creative writer who specializes in {input_data.reference_type} style writing."},
            {"role": "user", "content": prompt}
        ]
    )

    state["theme_reference"] = f"{input_data.reference_type}"
    state["blog_content"] = response.choices[0].message.content
    return state

def process_publish_node(state: Dict, input_data: PublishNode) -> Dict:
    if not state.get("blog_content"):
        raise HTTPException(status_code=400, detail="Blog content must be generated first")

    # Initialize Hashnode client
    hashnode_client = HashnodeClient(os.getenv("HASHNODE_API_KEY"))
    
    try:
        response = hashnode_client.create_post(
            title=state["blog_topic"],
            content=state["blog_content"],
            tags=[],
            is_draft=True if input_data.schedule_time else False,
            scheduled_time=input_data.schedule_time.isoformat() if input_data.schedule_time else None
        )
        state["published_date"] = input_data.schedule_time
        state["status"] = "published"
        state["post_id"] = response.get("post", {}).get("_id")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish to Hashnode: {str(e)}")
    return state

def process_tweet_node(state: Dict, input_data: TweetNode) -> Dict:
    if not state.get("blog_content"):
        raise HTTPException(status_code=400, detail="Blog content must be generated first")
    
    prompt = f"Convert this blog post into a Twitter thread (max 10 tweets):\n{state['blog_content']}"

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Create an engaging Twitter thread from the given blog post."},
            {"role": "user", "content": prompt}
        ]
    )

    thread = response.choices[0].message.content.split('\n\n')
    
    # Uncomment to enable Twitter posting
    # auth = tweepy.OAuthHandler(os.getenv("TWITTER_API_KEY"), os.getenv("TWITTER_API_SECRET"))
    # auth.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_TOKEN_SECRET"))
    # twitter_api = tweepy.API(auth)
    
    # previous_tweet_id = None
    # for tweet in thread:
    #     status = twitter_api.update_status(status=tweet, in_reply_to_status_id=previous_tweet_id)
    #     previous_tweet_id = status.id
    
    state["tweet_thread"] = thread
    return state

# API Endpoints
@app.post("/workflow/blog", response_model=WorkflowState)
async def create_blog(blog_input: BlogNode):
    state = {"status": "pending"}
    state = process_blog_node(state, blog_input)
    return WorkflowState(**state)

@app.post("/workflow/theme", response_model=WorkflowState)
async def apply_theme(theme_input: ThemeNode):
    state = {"status": "pending"}
    state = process_theme_node(state, theme_input)
    return WorkflowState(**state)

@app.post("/workflow/publish", response_model=WorkflowState)
async def publish_blog(publish_input: PublishNode):
    state = {"status": "pending"}
    state = process_publish_node(state, publish_input)
    return WorkflowState(**state)

@app.post("/workflow/tweet", response_model=WorkflowState)
async def create_tweet_thread(tweet_input: TweetNode):
    state = {"status": "pending"}
    state = process_tweet_node(state, tweet_input)
    return WorkflowState(**state)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)