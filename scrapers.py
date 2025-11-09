"""
Data Scraping Module
Handles scraping from Reddit, Twitter, and News sources
"""

import os
import praw
import tweepy
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============= REDDIT SCRAPER =============

class RedditScraper:
    def __init__(self):
        """Initialize Reddit API connection"""
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT'),
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD')
        )
        logger.info("✅ Reddit API initialized")
    
    def scrape_stock_subreddits(self, stock_ticker: str, limit: int = 100) -> list:
        """
        Scrape stock-related subreddits for mentions of stock_ticker
        
        Args:
            stock_ticker: Stock symbol (e.g., 'AAPL', 'TSLA')
            limit: Number of posts to fetch
        
        Returns:
            List of dicts with format: {'text': str, 'source': 'reddit', 'timestamp': datetime}
        """
        posts = []
        subreddits = ['wallstreetbets', 'stocks', 'investing', 'stocks', 'options']
        
        try:
            for subreddit_name in subreddits:
                logger.info(f"🔍 Scraping r/{subreddit_name} for {stock_ticker}...")
                
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search for posts mentioning the stock
                search_results = subreddit.search(stock_ticker, time_filter='week', limit=limit)
                
                for post in search_results:
                    posts.append({
                        'text': f"{post.title} {post.selftext}",  # Combine title and content
                        'source': 'reddit',
                        'subreddit': subreddit_name,
                        'author': post.author,
                        'score': post.score,
                        'timestamp': datetime.fromtimestamp(post.created_utc),
                        'url': post.url
                    })
            
            logger.info(f"✅ Found {len(posts)} Reddit posts about {stock_ticker}")
            return posts
            
        except Exception as e:
            logger.error(f"❌ Reddit scraping error: {str(e)}")
            return []


# ============= TWITTER/X SCRAPER =============

class TwitterScraper:
    def __init__(self):
        """Initialize Twitter API v2 connection"""
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.client = tweepy.Client(bearer_token=self.bearer_token)
        logger.info("✅ Twitter API initialized")
    
    def scrape_tweets(self, stock_ticker: str, max_results: int = 100) -> list:
        """
        Scrape tweets mentioning stock ticker
        
        Args:
            stock_ticker: Stock symbol or company name
            max_results: Number of tweets to fetch (max 100 for free tier)
        
        Returns:
            List of dicts with format: {'text': str, 'source': 'twitter', 'timestamp': datetime}
        """
        tweets = []
        
        try:
            # Add $ to get official ticker mentions
            query = f"${stock_ticker} -is:retweet lang:en"
            
            logger.info(f"🔍 Scraping Twitter for {query}...")
            
            # Search recent tweets (free tier limited to 7 days)
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics'],
                expansions=['author_id'],
                user_fields=['username']
            )
            
            if response.data:
                for tweet in response.data:
                    tweets.append({
                        'text': tweet.text,
                        'source': 'twitter',
                        'id': tweet.id,
                        'timestamp': tweet.created_at,
                        'url': f"https://twitter.com/i/web/status/{tweet.id}"
                    })
            
            logger.info(f"✅ Found {len(tweets)} tweets about {stock_ticker}")
            return tweets
            
        except Exception as e:
            logger.error(f"❌ Twitter scraping error: {str(e)}")
            return []


# ============= NEWS SCRAPER =============

class NewsScraper:
    def __init__(self):
        """Initialize news scraper"""
        # TODO: Add NEWS_API_KEY to .env if using NewsAPI
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        logger.info("✅ News API initialized")
    
    def scrape_financial_news(self, company_name: str, max_results: int = 50) -> list:
        """
        Scrape financial news about company
        
        Args:
            company_name: Company name (e.g., 'Apple Inc')
            max_results: Number of articles to fetch
        
        Returns:
            List of dicts with format: {'text': str, 'source': 'news', 'timestamp': datetime}
        """
        articles = []
        
        # TODO: Implement news scraping if using NewsAPI
        # For now, returning empty list as placeholder
        logger.info(f"📰 News scraping for {company_name} (TODO: implement with NewsAPI)")
        
        return articles


# ============= UNIFIED SCRAPER =============

class UnifiedScraper:
    def __init__(self):
        """Initialize all scrapers"""
        self.reddit = RedditScraper()
        self.twitter = TwitterScraper()
        self.news = NewsScraper()
    
    def scrape_all(self, stock_ticker: str, reddit_limit: int = 50, 
                   twitter_limit: int = 100, news_limit: int = 30) -> list:
        """
        Scrape all sources for stock information
        
        Args:
            stock_ticker: Stock symbol
            reddit_limit: Number of Reddit posts
            twitter_limit: Number of tweets
            news_limit: Number of news articles
        
        Returns:
            Combined list of all scraped data
        """
        logger.info(f"\n🚀 Starting unified scrape for {stock_ticker}...\n")
        
        all_data = []
        
        # Scrape Reddit
        reddit_data = self.reddit.scrape_stock_subreddits(stock_ticker, limit=reddit_limit)
        all_data.extend(reddit_data)
        
        # Scrape Twitter
        twitter_data = self.twitter.scrape_tweets(stock_ticker, max_results=twitter_limit)
        all_data.extend(twitter_data)
        
        # Scrape News
        news_data = self.news.scrape_financial_news(stock_ticker, max_results=news_limit)
        all_data.extend(news_data)
        
        logger.info(f"\n✅ Total data points collected: {len(all_data)}\n")
        
        return all_data


# Test the scrapers
if __name__ == "__main__":
    scraper = UnifiedScraper()
    data = scraper.scrape_all("AAPL", reddit_limit=10, twitter_limit=20)
    for item in data[:3]:
        print(f"Source: {item['source']} | Text: {item['text'][:100]}...")
