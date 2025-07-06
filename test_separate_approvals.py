#!/usr/bin/env python3
"""
Test script to verify separate Hashnode and Twitter approval workflow
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
        "topic": "The Future of Artificial Intelligence",
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
    print("=== Testing Separate Hashnode and Twitter Approvals ===")
    
    # Start workflow
    thread_id = start_workflow()
    if not thread_id:
        return
    
    # Wait for workflow to process
    print("\nWaiting for workflow to process...")
    time.sleep(5)
    
    # Check initial status
    print("\n=== Step 1: Check Initial Status ===")
    status = get_workflow_status(thread_id)
    
    current_node = status.get("current_node", "")
    workflow_status = status.get("status", "")
    requires_input = status.get("requires_human_input", False)
    
    print(f"Current node: {current_node}")
    print(f"Workflow status: {workflow_status}")
    print(f"Requires human input: {requires_input}")
    
    # Step 1: Approve Hashnode
    if current_node == "hashnode_post" and requires_input:
        print("\n=== Step 2: Approve Hashnode Publishing ===")
        hashnode_result = approve_hashnode(thread_id)
        
        if hashnode_result:
            # Wait for Hashnode processing
            print("\nWaiting for Hashnode publishing...")
            time.sleep(10)
            
            # Check status after Hashnode
            print("\n=== Step 3: Check Status After Hashnode ===")
            status_after_hashnode = get_workflow_status(thread_id)
            
            current_node = status_after_hashnode.get("current_node", "")
            workflow_status = status_after_hashnode.get("status", "")
            requires_input = status_after_hashnode.get("requires_human_input", False)
            
            print(f"Current node: {current_node}")
            print(f"Workflow status: {workflow_status}")
            print(f"Requires human input: {requires_input}")
            
            # Step 2: Handle Twitter approval
            if current_node == "twitter_post" and requires_input:
                print("\n=== Step 4: Twitter Approval Decision ===")
                print("Choose Twitter action:")
                print("1. Approve Twitter publishing")
                print("2. Reject Twitter publishing")
                
                choice = input("Enter choice (1 or 2): ").strip()
                
                if choice == "1":
                    print("\n=== Step 5: Approve Twitter Publishing ===")
                    twitter_result = approve_twitter(thread_id)
                    
                    if twitter_result:
                        print("\nWaiting for Twitter publishing...")
                        time.sleep(10)
                        
                        # Final status
                        print("\n=== Step 6: Final Status ===")
                        final_status = get_workflow_status(thread_id)
                        print(f"Final workflow status: {json.dumps(final_status, indent=2)}")
                        
                elif choice == "2":
                    print("\n=== Step 5: Reject Twitter Publishing ===")
                    twitter_result = reject_twitter(thread_id)
                    
                    if twitter_result:
                        print("\n=== Step 6: Final Status ===")
                        final_status = get_workflow_status(thread_id)
                        print(f"Final workflow status: {json.dumps(final_status, indent=2)}")
                else:
                    print("Invalid choice. Exiting.")
            else:
                print(f"❌ Expected Twitter approval step, but got: {current_node}")
                print("This indicates the separate approval logic may not be working correctly.")
        else:
            print("❌ Failed to approve Hashnode publishing")
    else:
        print(f"❌ Expected Hashnode approval step, but got: {current_node}")
        print("This indicates the workflow may not be pausing correctly for Hashnode approval.")

if __name__ == "__main__":
    main()
