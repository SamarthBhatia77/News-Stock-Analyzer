import praw
import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

# Reddit scraper using PRAW
def scrape_reddit_stock_discussions(stock_symbol, company_name, limit=50):
    """
    Scrapes Reddit for stock discussions
    Returns list of post titles and top comments
    """
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )
    
    # Search relevant subreddits
    subreddits = ['stocks', 'investing', 'wallstreetbets', 'StockMarket']
    
    posts = []
    query = f"{stock_symbol} OR {company_name}"
    
    for subreddit_name in subreddits:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            
            # Search for posts about the stock
            for submission in subreddit.search(query, limit=limit, time_filter='week'):
                # Add post title
                posts.append(submission.title)
                
                # Add top comment if exists
                submission.comments.replace_more(limit=0)
                if submission.comments:
                    top_comment = submission.comments[0].body
                    posts.append(top_comment)
        
        except Exception as e:
            print(f"Error scraping r/{subreddit_name}: {str(e)}")
            continue
    
    print(f"✓ Scraped {len(posts)} texts from Reddit")
    return posts


# Twitter/X scraper using Tweepy
def scrape_twitter_stock_tweets(stock_symbol, company_name, limit=50):
    """
    Scrapes Twitter/X for stock-related tweets
    Returns list of tweet texts
    """
    # Twitter API v2 authentication
    client = tweepy.Client(
        bearer_token=os.getenv('TWITTER_BEARER_TOKEN')
    )
    
    # Search query
    query = f"({stock_symbol} OR {company_name}) (stock OR investing OR trading) -is:retweet"
    
    tweets = []
    
    try:
        # Search recent tweets
        response = client.search_recent_tweets(
            query=query,
            max_results=min(limit, 100),  # Twitter API limit
            tweet_fields=['created_at', 'public_metrics']
        )
        
        if response.data:
            for tweet in response.data:
                tweets.append(tweet.text)
        
        print(f"✓ Scraped {len(tweets)} tweets from X/Twitter")
        
    except Exception as e:
        print(f"Error scraping Twitter: {str(e)}")
    
    return tweets


def scrape_all_sources(stock_symbol, company_name):
    """
    Scrapes both Reddit and Twitter
    Returns combined list of texts
    """
    print(f"\n[1/5] Scraping social media for {company_name} ({stock_symbol})...")
    
    reddit_posts = scrape_reddit_stock_discussions(stock_symbol, company_name, limit=30)
    twitter_tweets = scrape_twitter_stock_tweets(stock_symbol, company_name, limit=30)
    
    all_texts = reddit_posts + twitter_tweets
    
    print(f"✓ Total texts scraped: {len(all_texts)}")
    return all_texts
