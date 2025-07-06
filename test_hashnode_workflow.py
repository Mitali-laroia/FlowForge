#!/usr/bin/env python3
"""
Test script to trigger the complete workflow including both Hashnode and Twitter publishing
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
        "user_id": "test_user_123",
        "topic": "Artificial Intelligence in Healthcare",
        "theme": None
    }
    
    print("Starting workflow...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Workflow started successfully!")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result.get("thread_id")
    else:
        print(f"Failed to start workflow: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def provide_human_input(thread_id, user_input="yes", action="approve"):
    """Provide human input to continue workflow"""
    url = f"{BASE_URL}/workflows/{thread_id}/input"
    payload = {
        "thread_id": thread_id,
        "user_input": user_input,
        "action": action
    }
    
    print(f"\nProviding human input...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Human input provided successfully!")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"Failed to provide human input: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def get_workflow_status(thread_id):
    """Get workflow status"""
    url = f"{BASE_URL}/workflows/{thread_id}/status"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Workflow status: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"Failed to get workflow status: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def approve_hashnode(thread_id):
    """Approve Hashnode publishing using specific endpoint"""
    url = f"{BASE_URL}/workflows/{thread_id}/approve/hashnode"

    print(f"\nApproving Hashnode publishing...")

    response = requests.post(url)

    if response.status_code == 200:
        result = response.json()
        print(f"Hashnode approved successfully!")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"Failed to approve Hashnode: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def approve_twitter(thread_id):
    """Approve Twitter publishing using specific endpoint"""
    url = f"{BASE_URL}/workflows/{thread_id}/approve/twitter"

    print(f"\nApproving Twitter publishing...")

    response = requests.post(url)

    if response.status_code == 200:
        result = response.json()
        print(f"Twitter approved successfully!")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"Failed to approve Twitter: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def reject_twitter(thread_id):
    """Reject Twitter publishing using specific endpoint"""
    url = f"{BASE_URL}/workflows/{thread_id}/reject/twitter"

    print(f"\nRejecting Twitter publishing...")

    response = requests.post(url)

    if response.status_code == 200:
        result = response.json()
        print(f"Twitter rejected successfully!")
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"Failed to reject Twitter: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def main():
    """Main test function"""
    print("=== Testing Complete Workflow (Hashnode + Twitter) ===")

    # Start workflow
    thread_id = start_workflow()
    if not thread_id:
        return

    # Wait a bit for workflow to process
    print("\nWaiting for workflow to process...")
    time.sleep(5)

    # Check status
    print("\n=== Checking Initial Workflow Status ===")
    status = get_workflow_status(thread_id)

    # Check if workflow is waiting for Hashnode approval
    current_node = status.get("current_node", "")
    workflow_status = status.get("status", "")

    print(f"Current node: {current_node}")
    print(f"Workflow status: {workflow_status}")
    print(f"Requires human input: {status.get('requires_human_input')}")

    # Step 1: Handle Hashnode approval
    if current_node == "hashnode_post" or "waiting_hashnode_approval" in workflow_status:
        print("\n=== STEP 1: Hashnode Publishing ===")
        result = approve_hashnode(thread_id)

        if result:
            # Wait for Hashnode processing
            print("\nWaiting for Hashnode publishing...")
            time.sleep(10)

            # Check status after Hashnode
            print("\n=== Status After Hashnode Publishing ===")
            hashnode_status = get_workflow_status(thread_id)

            # Step 2: Handle Twitter approval
            current_node = hashnode_status.get("current_node", "")
            workflow_status = hashnode_status.get("status", "")

            if current_node == "twitter_post" or "waiting_twitter_approval" in workflow_status:
                print("\n=== STEP 2: Twitter Publishing ===")

                # Ask user what to do with Twitter
                print("\nOptions for Twitter:")
                print("1. Approve Twitter publishing")
                print("2. Reject Twitter publishing")
                choice = input("Enter choice (1 or 2): ").strip()

                if choice == "1":
                    twitter_result = approve_twitter(thread_id)
                    if twitter_result:
                        print("\nWaiting for Twitter publishing...")
                        time.sleep(10)
                else:
                    twitter_result = reject_twitter(thread_id)

                # Final status check
                print("\n=== Final Workflow Status ===")
                final_status = get_workflow_status(thread_id)
                print(f"Final status: {json.dumps(final_status, indent=2)}")
            else:
                print(f"Unexpected workflow state after Hashnode: {current_node}")
        else:
            print("Failed to approve Hashnode publishing")
    else:
        print(f"Unexpected initial workflow state: {current_node}")

def test_twitter_only():
    """Test Twitter publishing functionality separately"""
    print("\n=== Testing Twitter Service Separately ===")

    # Test the Twitter service directly
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.getcwd(), 'Backend'))
        from app.services.twitter_service import TwitterService

        twitter_service = TwitterService()

        # Test credentials
        print("Testing Twitter credentials...")
        creds_result = twitter_service.verify_credentials()
        print(f"Credentials result: {json.dumps(creds_result, indent=2)}")

        # Test thread posting
        sample_thread = """
        1/3 🧵 Artificial Intelligence is revolutionizing healthcare! From diagnostic imaging to personalized treatment plans, AI is making medicine more precise and accessible. #AI #Healthcare #Innovation

        2/3 Telemedicine platforms powered by AI can now provide preliminary diagnoses, monitor chronic conditions remotely, and even predict health risks before symptoms appear. This is the future of preventive care! 🏥💡

        3/3 As we embrace these technologies, we must ensure they remain ethical, accessible, and human-centered. The goal is to augment human expertise, not replace it. What are your thoughts on AI in healthcare? 🤔 #HealthTech #FutureOfMedicine
        """

        print("\nTesting Twitter thread posting...")
        thread_result = twitter_service.post_thread(sample_thread)
        print(f"Thread result: {json.dumps(thread_result, indent=2)}")

    except Exception as e:
        print(f"Error testing Twitter service: {str(e)}")

if __name__ == "__main__":
    # Run main workflow test
    main()

    # Optionally test Twitter service separately
    print("\n" + "="*50)
    test_twitter_only()

if __name__ == "__main__":
    main()
