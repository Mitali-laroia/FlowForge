"""
Twitter API service for publishing tweets and threads
"""

import tweepy
import json
import time
from typing import Dict, Any, List
from ..core.config import settings


class TwitterService:
    def __init__(self):
        """Initialize Twitter API client"""
        self.api_key = settings.TWITTER_API_KEY
        self.api_secret = settings.TWITTER_API_SECRET
        self.access_token = settings.TWITTER_ACCESS_TOKEN
        self.access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET

        # Check if we have real credentials or should use mock mode
        self.mock_mode = (
            not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]) or
            self.api_key.startswith("your_") or
            self.api_secret.startswith("your_") or
            self.access_token.startswith("your_") or
            self.access_token_secret.startswith("your_")
        )

        if self.mock_mode:
            print("Twitter API running in MOCK MODE - no real tweets will be posted")
            self.client = None
        else:
            # Initialize Twitter API v2 client
            self.client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            print(f"Twitter API initialized with API key: {self.api_key[:10]}...")
    
    def verify_credentials(self) -> Dict[str, Any]:
        """Verify Twitter API credentials"""
        if self.mock_mode:
            return {
                "success": True,
                "mock": True,
                "user": {
                    "id": "mock_user_123",
                    "username": "mock_user",
                    "name": "Mock Twitter User"
                }
            }

        try:
            user = self.client.get_me()
            if user.data:
                return {
                    "success": True,
                    "user": {
                        "id": user.data.id,
                        "username": user.data.username,
                        "name": user.data.name
                    }
                }
            else:
                return {"success": False, "message": "Failed to get user data"}
        except Exception as e:
            return {"success": False, "message": f"Twitter API error: {str(e)}"}
    
    def parse_thread_content(self, thread_content: str) -> List[str]:
        """Parse thread content into individual tweets"""
        # Split by lines and filter out empty lines
        lines = [line.strip() for line in thread_content.split('\n') if line.strip()]
        
        tweets = []
        current_tweet = ""
        
        for line in lines:
            # Check if line starts with a number (like "1/5", "2/5", etc.)
            if any(line.startswith(f"{i}/") for i in range(1, 21)):  # Support up to 20 tweets
                # If we have a current tweet, save it
                if current_tweet.strip():
                    tweets.append(current_tweet.strip())
                # Start new tweet
                current_tweet = line
            else:
                # Continue current tweet
                if current_tweet:
                    current_tweet += " " + line
                else:
                    current_tweet = line
        
        # Add the last tweet
        if current_tweet.strip():
            tweets.append(current_tweet.strip())
        
        # Clean up tweets and ensure they're under 280 characters
        cleaned_tweets = []
        for tweet in tweets:
            # Remove thread numbering for actual posting
            # Keep only the content after the numbering
            if any(tweet.startswith(f"{i}/") for i in range(1, 21)):
                parts = tweet.split(' ', 1)
                if len(parts) > 1:
                    tweet = parts[1]
            
            # Ensure tweet is under 280 characters
            if len(tweet) > 280:
                tweet = tweet[:277] + "..."
            
            cleaned_tweets.append(tweet)
        
        return cleaned_tweets
    
    def post_thread(self, thread_content: str) -> Dict[str, Any]:
        """Post a Twitter thread"""
        try:
            print(f"Posting Twitter thread...")
            print(f"Thread content: {thread_content[:200]}...")

            # Parse the thread content into individual tweets
            tweets = self.parse_thread_content(thread_content)

            if not tweets:
                return {"success": False, "message": "No valid tweets found in thread content"}

            print(f"Parsed {len(tweets)} tweets from thread")

            # Handle mock mode
            if self.mock_mode:
                print("MOCK MODE: Simulating Twitter thread posting...")
                mock_tweets = []
                for i, tweet_text in enumerate(tweets):
                    mock_tweet_id = f"mock_tweet_{int(time.time())}_{i}"
                    mock_tweets.append({
                        "id": mock_tweet_id,
                        "text": tweet_text,
                        "url": f"https://twitter.com/mock_user/status/{mock_tweet_id}"
                    })
                    print(f"MOCK: Posted tweet {i+1}/{len(tweets)}: {tweet_text[:50]}...")

                return {
                    "success": True,
                    "mock": True,
                    "message": f"MOCK: Successfully posted {len(mock_tweets)} tweets",
                    "tweets": mock_tweets,
                    "thread_url": mock_tweets[0]["url"] if mock_tweets else None
                }
            
            posted_tweets = []
            reply_to_id = None
            
            for i, tweet_text in enumerate(tweets):
                print(f"Posting tweet {i+1}/{len(tweets)}: {tweet_text[:50]}...")
                
                try:
                    # Post the tweet
                    if reply_to_id:
                        # Reply to previous tweet in thread
                        response = self.client.create_tweet(
                            text=tweet_text,
                            in_reply_to_tweet_id=reply_to_id
                        )
                    else:
                        # First tweet in thread
                        response = self.client.create_tweet(text=tweet_text)
                    
                    if response.data:
                        tweet_id = response.data['id']
                        reply_to_id = tweet_id  # Next tweet will reply to this one
                        
                        posted_tweets.append({
                            "id": tweet_id,
                            "text": tweet_text,
                            "url": f"https://twitter.com/user/status/{tweet_id}"
                        })
                        
                        print(f"Successfully posted tweet {i+1}: {tweet_id}")
                        
                        # Add delay between tweets to avoid rate limiting
                        if i < len(tweets) - 1:  # Don't delay after last tweet
                            time.sleep(2)
                    else:
                        print(f"Failed to post tweet {i+1}: No response data")
                        break
                        
                except Exception as tweet_error:
                    print(f"Error posting tweet {i+1}: {str(tweet_error)}")
                    break
            
            if posted_tweets:
                return {
                    "success": True,
                    "message": f"Successfully posted {len(posted_tweets)} tweets",
                    "tweets": posted_tweets,
                    "thread_url": posted_tweets[0]["url"] if posted_tweets else None
                }
            else:
                return {"success": False, "message": "Failed to post any tweets"}
                
        except Exception as e:
            error_message = f"Twitter API error: {str(e)}"
            print(error_message)
            return {"success": False, "message": error_message}
    
    def post_single_tweet(self, content: str) -> Dict[str, Any]:
        """Post a single tweet"""
        try:
            print(f"Posting single tweet: {content[:50]}...")

            # Ensure tweet is under 280 characters
            if len(content) > 280:
                content = content[:277] + "..."

            # Handle mock mode
            if self.mock_mode:
                print("MOCK MODE: Simulating single tweet posting...")
                mock_tweet_id = f"mock_tweet_{int(time.time())}"
                return {
                    "success": True,
                    "mock": True,
                    "message": "MOCK: Tweet posted successfully",
                    "tweet": {
                        "id": mock_tweet_id,
                        "text": content,
                        "url": f"https://twitter.com/mock_user/status/{mock_tweet_id}"
                    }
                }

            response = self.client.create_tweet(text=content)
            
            if response.data:
                tweet_id = response.data['id']
                return {
                    "success": True,
                    "message": "Tweet posted successfully",
                    "tweet": {
                        "id": tweet_id,
                        "text": content,
                        "url": f"https://twitter.com/user/status/{tweet_id}"
                    }
                }
            else:
                return {"success": False, "message": "Failed to post tweet: No response data"}
                
        except Exception as e:
            error_message = f"Twitter API error: {str(e)}"
            print(error_message)
            return {"success": False, "message": error_message}
