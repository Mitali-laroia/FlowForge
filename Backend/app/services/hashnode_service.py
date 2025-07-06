import httpx
from typing import Dict, Any, Optional
from ..core.config import settings
import json

class HashnodeService:
    def __init__(self):
        self.api_key = settings.HASHNODE_API_KEY
        self.base_url = "https://gql.hashnode.com"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key
        }
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get user information from Hashnode"""
        query = """
        query {
            me {
                id
                username
                name
                publications(first: 10) {
                    edges {
                        node {
                            id
                            title
                            url
                        }
                        role
                    }
                }
            }
        }
        """
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.base_url}/graphql",
                headers=self.headers,
                json={"query": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for GraphQL errors
                if data.get("errors"):
                    error_messages = [error.get("message", "Unknown error") for error in data.get("errors", [])]
                    raise Exception(f"GraphQL errors: {'; '.join(error_messages)}")
                
                return data.get("data", {}).get("me", {})
            else:
                raise Exception(f"Failed to get user info: {response.text}")
    
    def create_post(self, title: str, content: str, tags: list, is_republished: bool = False) -> Dict[str, Any]:
        """Create a new post on Hashnode"""
        print(f"Creating post with title: {title}")
        print(f"Content length: {len(content)}")
        print(f"Tags: {tags}")
        print(f"API Key: {self.api_key[:10]}..." if self.api_key else "No API key")
        
        # First get user info to get publication ID
        try:
            user_info = self.get_user_info()
            user_id = user_info.get("id")
            
            # Get the first publication from the user
            publications = user_info.get("publications", {}).get("edges", [])
            if not publications:
                raise Exception("No publications found for user")
            
            publication = publications[0]["node"]
            publication_id = publication.get("id")
            
            if not publication_id:
                raise Exception("Publication ID not found in user info")
            
            print(f"Publication ID: {publication_id}")
            print(f"User ID: {user_id}")
            print(f"Publication Title: {publication.get('title')}")
            print(f"Publication URL: {publication.get('url')}")
            
        except Exception as e:
            print(f"Failed to get user info: {e}")
            # Fallback to using settings if available
            publication_id = settings.HASHNODE_PUBLICATION_ID
            user_id = None
            
            if not publication_id:
                raise Exception("No publication ID available. Please set HASHNODE_PUBLICATION_ID in your .env file")
        
        # Process tags to include both name and slug
        processed_tags = []
        for tag in tags:
            if isinstance(tag, str):
                # Convert tag name to slug format
                slug = tag.lower().replace(' ', '-').replace('_', '-')
                processed_tags.append({
                    "name": tag,
                    "slug": slug
                })
            elif isinstance(tag, dict):
                # If tag is already a dict, ensure it has both name and slug
                tag_name = tag.get("name", "blog")
                tag_slug = tag.get("slug", tag_name.lower().replace(' ', '-').replace('_', '-'))
                processed_tags.append({
                    "name": tag_name,
                    "slug": tag_slug
                })
        
        # If no tags provided, add a default tag
        if not processed_tags:
            processed_tags = [{"name": "blog", "slug": "blog"}]
        
        print(f"Processed tags: {processed_tags}")
        
        # Updated GraphQL query for Hashnode - removed contentMarkdown field
        query = """
        mutation CreateDraft($input: CreateDraftInput!) {
            createDraft(input: $input) {
                draft {
                    id
                    title
                    slug
                    tags {
                        name
                        slug
                    }
                    dateUpdated
                }
            }
        }
        """
        
        variables = {
            "input": {
                "title": title,
                "contentMarkdown": content,
                "tags": processed_tags,
                "publicationId": publication_id,
                "publishAs": user_id  # Use the actual user ID
            }
        }
        
        print(f"Making request to: {self.base_url}/graphql")
        print(f"Variables: {json.dumps(variables, indent=2)}")
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.base_url}/graphql",
                headers=self.headers,
                json={
                    "query": query,
                    "variables": variables
                }
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for GraphQL errors
                if data.get("errors"):
                    error_messages = [error.get("message", "Unknown error") for error in data.get("errors", [])]
                    raise Exception(f"GraphQL errors: {'; '.join(error_messages)}")
                
                result = data.get("data", {}).get("createDraft", {})
                
                if result.get("draft"):
                    draft = result.get("draft", {})
                    return {
                        "success": True,
                        "draft_id": draft.get("id"),
                        "title": draft.get("title"),
                        "slug": draft.get("slug"),
                        "message": "Draft created successfully"
                    }
                else:
                    raise Exception(f"Failed to create draft: {data}")
            else:
                raise Exception(f"API request failed: {response.text}")
    
    def publish_draft(self, draft_id: str) -> Dict[str, Any]:
        """Publish a draft post"""
        print(f"Publishing draft with ID: {draft_id}")

        query = """
        mutation PublishDraft($input: PublishDraftInput!) {
            publishDraft(input: $input) {
                post {
                    id
                    title
                    slug
                    url
                    publishedAt
                    tags {
                        name
                        slug
                    }
                }
            }
        }
        """

        variables = {
            "input": {
                "draftId": draft_id
            }
        }

        print(f"Publish variables: {json.dumps(variables, indent=2)}")

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.base_url}/graphql",
                headers=self.headers,
                json={
                    "query": query,
                    "variables": variables
                }
            )

            print(f"Publish response status: {response.status_code}")
            print(f"Publish response body: {response.text}")

            if response.status_code == 200:
                data = response.json()
                
                # Check for GraphQL errors
                if data.get("errors"):
                    error_messages = [error.get("message", "Unknown error") for error in data.get("errors", [])]
                    raise Exception(f"GraphQL errors: {'; '.join(error_messages)}")
                
                result = data.get("data", {}).get("publishDraft", {})
                
                if result.get("post"):
                    post = result.get("post", {})
                    return {
                        "success": True,
                        "post": post,
                        "message": "Post published successfully"
                    }
                else:
                    raise Exception(f"Failed to publish post: {data}")
            else:
                raise Exception(f"API request failed: {response.text}")