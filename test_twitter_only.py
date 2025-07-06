#!/usr/bin/env python3
"""
Test script to check Twitter publishing specifically
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def start_workflow_and_skip_to_twitter():
    """Start workflow and get to Twitter approval step"""
    url = f"{BASE_URL}/workflows/start"
    payload = {
        "user_id": "twitter_test_user",
        "topic": "Testing Twitter Integration with Real API",
        "theme": None
    }
    
    print("🚀 Starting workflow...")
    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        print(f"❌ Failed to start workflow: {response.status_code}")
        return None
    
    result = response.json()
    thread_id = result.get("thread_id")
    print(f"✅ Workflow started: {thread_id}")
    
    # Wait for content generation
    print("⏳ Waiting for content generation...")
    time.sleep(8)
    
    # Approve Hashnode to get to Twitter step
    print("📝 Approving Hashnode to reach Twitter step...")
    hashnode_url = f"{BASE_URL}/workflows/{thread_id}/approve/hashnode"
    hashnode_response = requests.post(hashnode_url)
    
    if hashnode_response.status_code != 200:
        print(f"❌ Failed to approve Hashnode: {hashnode_response.status_code}")
        return None
    
    print("✅ Hashnode approved, waiting for Twitter step...")
    time.sleep(10)
    
    # Check if we're at Twitter approval step
    status_url = f"{BASE_URL}/workflows/{thread_id}/status"
    status_response = requests.get(status_url)
    
    if status_response.status_code == 200:
        status = status_response.json()
        current_node = status.get('current_node')
        requires_input = status.get('requires_human_input')
        
        print(f"Current node: {current_node}")
        print(f"Requires input: {requires_input}")
        
        if current_node == 'twitter_post' and requires_input:
            print("✅ Ready for Twitter approval!")
            return thread_id
        else:
            print(f"❌ Unexpected state: {current_node}")
            return None
    
    return None

def test_twitter_publishing(thread_id):
    """Test Twitter publishing with real credentials"""
    print("\n🐦 Testing Twitter publishing...")
    
    # Approve Twitter
    twitter_url = f"{BASE_URL}/workflows/{thread_id}/approve/twitter"
    print(f"Calling: {twitter_url}")
    
    response = requests.post(twitter_url)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Twitter approval response: {result}")
        
        # Wait for publishing
        print("⏳ Waiting for Twitter publishing...")
        time.sleep(15)
        
        # Check final status
        status_url = f"{BASE_URL}/workflows/{thread_id}/status"
        status_response = requests.get(status_url)
        
        if status_response.status_code == 200:
            final_status = status_response.json()
            print(f"\n📊 Final Status:")
            print(f"Current node: {final_status.get('current_node')}")
            print(f"Status: {final_status.get('status')}")
            
            # Look for Twitter post data
            state = final_status.get('state', {})
            channel_values = state.get('channel_values', {})
            twitter_post = channel_values.get('twitter_post', {})
            
            if isinstance(twitter_post, dict):
                print(f"\n🐦 Twitter Post Data:")
                print(f"Success: {twitter_post.get('success', 'Not set')}")
                print(f"Message: {twitter_post.get('message', 'No message')}")
                
                if twitter_post.get('thread_url'):
                    print(f"Thread URL: {twitter_post['thread_url']}")
                
                if twitter_post.get('tweets'):
                    tweets = twitter_post['tweets']
                    print(f"Number of tweets: {len(tweets)}")
                    if tweets:
                        print(f"First tweet URL: {tweets[0].get('url', 'No URL')}")
            
            return True
        else:
            print(f"❌ Failed to get final status: {status_response.status_code}")
            return False
    else:
        print(f"❌ Failed to approve Twitter: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def main():
    print("🧪 TWITTER-SPECIFIC TEST")
    print("=" * 50)
    print("This test will:")
    print("1. Start a workflow")
    print("2. Skip through to Twitter approval")
    print("3. Test Twitter publishing with real credentials")
    print("=" * 50)
    
    # Start workflow and get to Twitter step
    thread_id = start_workflow_and_skip_to_twitter()
    
    if thread_id:
        # Test Twitter publishing
        success = test_twitter_publishing(thread_id)
        
        if success:
            print("\n🎉 Twitter test completed!")
        else:
            print("\n❌ Twitter test failed!")
    else:
        print("\n❌ Failed to reach Twitter approval step!")

if __name__ == "__main__":
    main()
