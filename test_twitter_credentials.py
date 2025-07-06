#!/usr/bin/env python3
"""
Test script to verify Twitter API credentials and permissions
"""

import tweepy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_twitter_credentials():
    """Test Twitter API credentials"""
    print("🔍 Testing Twitter API Credentials")
    print("=" * 50)

    # Debug: Check if .env file exists and what it contains
    print("🔍 Debugging environment loading...")

    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found in current directory")
        with open('.env', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'TWITTER_API_KEY' in line:
                    print(f"📄 .env file contains: {line.strip()}")
    else:
        print("❌ .env file not found in current directory")

    # Get credentials from environment
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    print(f"\n🔍 Environment variables loaded:")
    print(f"API Key: {api_key[:10]}..." if api_key else "API Key: Not found")
    print(f"API Secret: {api_secret[:10]}..." if api_secret else "API Secret: Not found")
    print(f"Access Token: {access_token[:10]}..." if access_token else "Access Token: Not found")
    print(f"Access Token Secret: {access_token_secret[:10]}..." if access_token_secret else "Access Token Secret: Not found")

    # Expected values from .env file
    print(f"\n🎯 Expected values from .env:")
    print(f"Expected API Key: 381XozHiQv...")
    print(f"Expected API Secret: nj5h4dwgmA...")
    print(f"Expected Access Token: 1280055872...")
    print(f"Expected Access Token Secret: XTwUePqqmg...")
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("❌ Missing credentials!")
        return False
    
    try:
        # Initialize Twitter API v2 client
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        
        print("\n✅ Twitter client initialized successfully")
        
        # Test 1: Get user info
        print("\n📋 Test 1: Getting user information...")
        try:
            me = client.get_me()
            if me.data:
                print(f"✅ User: @{me.data.username} ({me.data.name})")
                print(f"   ID: {me.data.id}")
            else:
                print("❌ Could not get user information")
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
        
        # Test 2: Check if we can create tweets (this will tell us about write permissions)
        print("\n📝 Test 2: Checking write permissions...")
        try:
            # Try to create a test tweet (we'll delete it immediately)
            test_tweet_text = "🧪 Testing Twitter API integration - this tweet will be deleted shortly"
            
            print(f"Attempting to post test tweet: {test_tweet_text}")
            response = client.create_tweet(text=test_tweet_text)
            
            if response.data:
                tweet_id = response.data['id']
                print(f"✅ Successfully created test tweet: {tweet_id}")
                
                # Try to delete the test tweet
                try:
                    delete_response = client.delete_tweet(tweet_id)
                    if delete_response.data and delete_response.data['deleted']:
                        print(f"✅ Successfully deleted test tweet")
                    else:
                        print(f"⚠️  Test tweet created but couldn't delete it: https://twitter.com/user/status/{tweet_id}")
                except Exception as delete_error:
                    print(f"⚠️  Test tweet created but couldn't delete it: {delete_error}")
                    print(f"   Please manually delete: https://twitter.com/user/status/{tweet_id}")
                
                return True
            else:
                print("❌ Failed to create test tweet - no response data")
                return False
                
        except Exception as e:
            print(f"❌ Error creating test tweet: {e}")
            
            # Check if it's a permissions issue
            if "403" in str(e) or "Forbidden" in str(e):
                print("\n🔍 403 Forbidden Error Analysis:")
                print("This usually means one of the following:")
                print("1. Your Twitter app doesn't have write permissions")
                print("2. Your Twitter API access level is too low (Essential/Basic)")
                print("3. Your app needs to be approved for posting tweets")
                print("\n📋 To fix this:")
                print("1. Go to https://developer.twitter.com/en/portal/dashboard")
                print("2. Select your app")
                print("3. Go to 'Settings' tab")
                print("4. Under 'User authentication settings', ensure 'Read and write' is selected")
                print("5. If you're on Essential access, you might need to upgrade to Basic or higher")
                
            return False
    
    except Exception as e:
        print(f"❌ Failed to initialize Twitter client: {e}")
        return False

def main():
    success = test_twitter_credentials()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Twitter API credentials are working correctly!")
        print("✅ You can post tweets with these credentials")
    else:
        print("❌ Twitter API credentials have issues")
        print("🔧 Please check the error messages above and fix the issues")

if __name__ == "__main__":
    main()
