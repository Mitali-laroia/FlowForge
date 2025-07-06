#!/usr/bin/env python3
"""
Test script to check if credentials are loaded correctly
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def check_twitter_credentials():
    """Check Twitter credentials status"""
    url = f"{BASE_URL}/health"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return

    # Let's create a simple endpoint to check credentials
    print("\n🔍 Checking Twitter credentials...")
    
    # We'll check the logs to see what's happening
    print("Please check the backend logs for Twitter initialization messages.")
    print("If you see 'Twitter API running in MOCK MODE', then credentials aren't loaded properly.")
    print("If you see 'Twitter API initialized with API key: ...', then credentials are loaded.")

def main():
    print("🔍 CREDENTIALS CHECK")
    print("=" * 50)
    
    check_twitter_credentials()
    
    print("\n📋 TROUBLESHOOTING STEPS:")
    print("1. Check that your .env file has real Twitter credentials")
    print("2. Ensure credentials don't start with 'your_'")
    print("3. Restart the backend: docker-compose restart backend")
    print("4. Check backend logs: docker-compose logs backend")

if __name__ == "__main__":
    main()
