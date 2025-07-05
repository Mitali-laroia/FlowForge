from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from app.models.models import User, Workflow, WorkflowExecution, NodeTemplate, WorkflowCheckpoint
from app.core.config import settings
import asyncio
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db.database = db.client[settings.DATABASE_NAME]
        
        # Initialize Beanie
        await init_beanie(
            database=db.database,
            document_models=[
                User,
                Workflow, 
                WorkflowExecution,
                NodeTemplate,
                WorkflowCheckpoint
            ],
        )
        
        print("Connected to MongoDB successfully!")
        
        # Insert default node templates
        await create_default_node_templates()
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB!")

async def create_default_node_templates():
    """Create default node templates if they don't exist"""
    templates = [
        {
            "name": "start",
            "category": "trigger",
            "description": "Starts the workflow execution",
            "input_schema": {},
            "output_schema": {"user_id": "string"},
            "config_schema": {},
            "icon": "play",
            "color": "#10b981"
        },
        {
            "name": "generate_blog",
            "category": "ai",
            "description": "Generate blog content using AI",
            "input_schema": {"topic": "string"},
            "output_schema": {"blog_content": "string"},
            "config_schema": {"model": "string", "temperature": "number"},
            "icon": "edit",
            "color": "#3b82f6"
        },
        {
            "name": "apply_theme",
            "category": "ai",
            "description": "Apply theme to content",
            "input_schema": {"content": "string", "theme": "string"},
            "output_schema": {"themed_content": "string"},
            "config_schema": {"theme": "string"},
            "icon": "palette",
            "color": "#8b5cf6"
        },
        {
            "name": "create_twitter_thread",
            "category": "ai",
            "description": "Create Twitter thread from content",
            "input_schema": {"content": "string"},
            "output_schema": {"twitter_thread": "string"},
            "config_schema": {"max_tweets": "number"},
            "icon": "twitter",
            "color": "#1da1f2"
        },
        {
            "name": "publish_hashnode",
            "category": "publishing",
            "description": "Publish content to Hashnode",
            "input_schema": {"content": "string", "title": "string"},
            "output_schema": {"published_url": "string"},
            "config_schema": {"api_key": "string"},
            "icon": "hashnode",
            "color": "#2962ff"
        },
        {
            "name": "publish_twitter",
            "category": "publishing",
            "description": "Publish tweet thread to Twitter",
            "input_schema": {"thread": "string"},
            "output_schema": {"tweet_urls": "array"},
            "config_schema": {"api_key": "string"},
            "icon": "twitter",
            "color": "#1da1f2"
        }
    ]
    
    for template_data in templates:
        existing = await NodeTemplate.find_one({"name": template_data["name"]})
        if not existing:
            template = NodeTemplate(**template_data)
            await template.create()