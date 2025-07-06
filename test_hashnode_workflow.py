#!/usr/bin/env python3
"""
Test script to trigger the Hashnode workflow and debug the publishing issue
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

def main():
    """Main test function"""
    print("=== Testing Hashnode Workflow ===")
    
    # Start workflow
    thread_id = start_workflow()
    if not thread_id:
        return
    
    # Wait a bit for workflow to process
    print("\nWaiting for workflow to process...")
    time.sleep(5)
    
    # Check status
    print("\n=== Checking Workflow Status ===")
    status = get_workflow_status(thread_id)
    
    # Check if workflow is waiting for human input or if current node is hashnode_post
    current_node = status.get("state", {}).get("current_node", "")
    workflow_status = status.get("state", {}).get("workflow_status", "")

    print(f"Current node: {current_node}")
    print(f"Workflow status: {workflow_status}")
    print(f"Requires human input: {status.get('requires_human_input')}")

    if (status and status.get("requires_human_input")) or current_node == "hashnode_post" or "waiting_hashnode_approval" in workflow_status:
        print("\n=== Providing Human Input for Hashnode ===")
        result = provide_human_input(thread_id, "yes", "approve")
        
        if result:
            # Wait for processing
            print("\nWaiting for Hashnode publishing...")
            time.sleep(10)
            
            # Check final status
            print("\n=== Final Workflow Status ===")
            final_status = get_workflow_status(thread_id)
            
            # If still waiting for input (Twitter), provide it
            if final_status and final_status.get("requires_human_input"):
                print("\n=== Providing Human Input for Twitter ===")
                provide_human_input(thread_id, "no", "reject")
                
                # Final check
                time.sleep(5)
                print("\n=== Final Status After Twitter Input ===")
                get_workflow_status(thread_id)

if __name__ == "__main__":
    main()
