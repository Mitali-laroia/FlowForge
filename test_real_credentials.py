#!/usr/bin/env python3
"""
End-to-end test with real Hashnode and Twitter API credentials
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def start_workflow():
    """Start a new workflow"""
    url = f"{BASE_URL}/workflows/start"
    payload = {
        "user_id": "real_test_user",
        "topic": "The Impact of AI on Modern Software Development",
        "theme": None
    }
    
    print("🚀 Starting workflow with real credentials...")
    print(f"Topic: {payload['topic']}")
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Workflow started successfully!")
        print(f"Thread ID: {result.get('thread_id')}")
        print(f"Status: {result.get('status')}")
        return result.get("thread_id")
    else:
        print(f"❌ Failed to start workflow: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def get_workflow_status(thread_id):
    """Get workflow status"""
    url = f"{BASE_URL}/workflows/{thread_id}/status"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        print(f"❌ Failed to get workflow status: {response.status_code}")
        return None

def approve_hashnode(thread_id):
    """Approve Hashnode publishing"""
    url = f"{BASE_URL}/workflows/{thread_id}/approve/hashnode"
    
    print(f"\n📝 Approving Hashnode publishing...")
    
    response = requests.post(url)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Hashnode approved successfully!")
        return result
    else:
        print(f"❌ Failed to approve Hashnode: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def approve_twitter(thread_id):
    """Approve Twitter publishing"""
    url = f"{BASE_URL}/workflows/{thread_id}/approve/twitter"
    
    print(f"\n🐦 Approving Twitter publishing...")
    
    response = requests.post(url)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Twitter approved successfully!")
        return result
    else:
        print(f"❌ Failed to approve Twitter: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def display_status(status, step_name):
    """Display workflow status in a readable format"""
    print(f"\n📊 {step_name}")
    print(f"Current Node: {status.get('current_node', 'Unknown')}")
    print(f"Workflow Status: {status.get('status', 'Unknown')}")
    print(f"Requires Input: {status.get('requires_human_input', False)}")
    
    # Extract content from state if available
    state = status.get('state', {})
    channel_values = state.get('channel_values', {})
    
    # Show blog title if available
    hashnode_post = channel_values.get('hashnode_post', {})
    if isinstance(hashnode_post, dict) and hashnode_post.get('title'):
        print(f"Blog Title: {hashnode_post['title']}")
    
    # Show published URL if available
    if isinstance(hashnode_post, dict) and hashnode_post.get('url'):
        print(f"📝 Hashnode URL: {hashnode_post['url']}")
    
    # Show Twitter thread info if available
    twitter_post = channel_values.get('twitter_post', {})
    if isinstance(twitter_post, dict) and twitter_post.get('thread_url'):
        print(f"🐦 Twitter Thread: {twitter_post['thread_url']}")

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 REAL CREDENTIALS END-TO-END TEST")
    print("=" * 60)
    print("This test will:")
    print("1. Generate a blog post about AI in Software Development")
    print("2. Publish to your real Hashnode blog")
    print("3. Post to your real Twitter account")
    print("4. Show all URLs and results")
    print("=" * 60)
    
    # Confirm with user
    confirm = input("\n⚠️  This will make REAL posts to Hashnode and Twitter. Continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Test cancelled by user.")
        return
    
    # Step 1: Start workflow
    print("\n" + "="*50)
    print("STEP 1: Starting Workflow")
    print("="*50)
    
    thread_id = start_workflow()
    if not thread_id:
        return
    
    # Wait for content generation
    print("\n⏳ Waiting for AI to generate blog content and Twitter thread...")
    time.sleep(8)
    
    # Step 2: Check initial status
    print("\n" + "="*50)
    print("STEP 2: Checking Workflow Status")
    print("="*50)
    
    status = get_workflow_status(thread_id)
    if not status:
        return
    
    display_status(status, "Initial Status")
    
    # Step 3: Approve Hashnode
    if status.get('current_node') == 'hashnode_post' and status.get('requires_human_input'):
        print("\n" + "="*50)
        print("STEP 3: Hashnode Publishing")
        print("="*50)
        
        hashnode_result = approve_hashnode(thread_id)
        if hashnode_result:
            print("\n⏳ Publishing to Hashnode...")
            time.sleep(10)
            
            # Check status after Hashnode
            status_after_hashnode = get_workflow_status(thread_id)
            if status_after_hashnode:
                display_status(status_after_hashnode, "Status After Hashnode")
                
                # Step 4: Approve Twitter
                if (status_after_hashnode.get('current_node') == 'twitter_post' and 
                    status_after_hashnode.get('requires_human_input')):
                    
                    print("\n" + "="*50)
                    print("STEP 4: Twitter Publishing")
                    print("="*50)
                    
                    twitter_result = approve_twitter(thread_id)
                    if twitter_result:
                        print("\n⏳ Publishing to Twitter...")
                        time.sleep(10)
                        
                        # Final status
                        print("\n" + "="*50)
                        print("STEP 5: Final Results")
                        print("="*50)
                        
                        final_status = get_workflow_status(thread_id)
                        if final_status:
                            display_status(final_status, "Final Status")
                            
                            # Extract and display final URLs
                            state = final_status.get('state', {})
                            channel_values = state.get('channel_values', {})
                            
                            hashnode_post = channel_values.get('hashnode_post', {})
                            twitter_post = channel_values.get('twitter_post', {})
                            
                            print("\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
                            print("="*50)
                            
                            if isinstance(hashnode_post, dict) and hashnode_post.get('url'):
                                print(f"📝 Hashnode Blog Post: {hashnode_post['url']}")
                            
                            if isinstance(twitter_post, dict) and twitter_post.get('thread_url'):
                                print(f"🐦 Twitter Thread: {twitter_post['thread_url']}")
                            elif isinstance(twitter_post, dict) and twitter_post.get('tweets'):
                                tweets = twitter_post['tweets']
                                if tweets and len(tweets) > 0:
                                    print(f"🐦 Twitter Thread: {tweets[0].get('url', 'URL not available')}")
                            
                            print("="*50)
                        else:
                            print("❌ Failed to get final status")
                    else:
                        print("❌ Failed to approve Twitter")
                else:
                    print(f"❌ Unexpected state after Hashnode: {status_after_hashnode.get('current_node')}")
            else:
                print("❌ Failed to get status after Hashnode")
        else:
            print("❌ Failed to approve Hashnode")
    else:
        print(f"❌ Unexpected initial state: {status.get('current_node')}")

if __name__ == "__main__":
    main()
