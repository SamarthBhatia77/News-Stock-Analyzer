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
        subreddits = ['wallstreetbets', 'stocks', 'investing', 'stocks', 'options', 'IndianStreetBets', 'StockMarketIndia']
        
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
        """Initialize NewsAPI connection"""
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2/everything"
        
        if not self.news_api_key:
            logger.warning("⚠️  NEWS_API_KEY not found in .env - news scraping will be disabled")
        else:
            logger.info("✅ News API initialized")
    
    def scrape_financial_news(self, stock_ticker: str, max_results: int = 50) -> list:
        """
        Scrape financial news articles about stock ticker
        
        Args:
            stock_ticker: Stock symbol (e.g., 'AAPL', 'TSLA')
            max_results: Number of articles to fetch (max 100 for free tier)
        
        Returns:
            List of dicts with format: {'text': str, 'source': 'news', 'timestamp': datetime}
        """
        articles = []
        
        # Check if API key exists
        if not self.news_api_key:
            logger.warning(f"📰 News scraping skipped - no API key configured")
            return articles
        
        try:
            # Map stock ticker to company name for better search results
            company_map = {
                                # ========== MAGNIFICENT 7 (Big Tech) ==========
                                'AAPL': 'Apple',
                                'MSFT': 'Microsoft',
                                'GOOGL': 'Google',
                                'GOOG': 'Google',  # Alternative ticker
                                'AMZN': 'Amazon',
                                'NVDA': 'Nvidia',
                                'META': 'Meta',
                                'TSLA': 'Tesla',
                                
                                # ========== MEGA CAP TECH ==========
                                'NFLX': 'Netflix',
                                'AMD': 'AMD',
                                'INTC': 'Intel',
                                'ORCL': 'Oracle',
                                'CRM': 'Salesforce',
                                'ADBE': 'Adobe',
                                'CSCO': 'Cisco',
                                'AVGO': 'Broadcom',
                                'QCOM': 'Qualcomm',
                                'TXN': 'Texas Instruments',
                                'ASML': 'ASML',
                                'TSM': 'TSMC',
                                
                                # ========== SOCIAL MEDIA & ENTERTAINMENT ==========
                                'SNAP': 'Snapchat',
                                'PINS': 'Pinterest',
                                'SPOT': 'Spotify',
                                'RBLX': 'Roblox',
                                'MTCH': 'Match Group',
                                'UBER': 'Uber',
                                'LYFT': 'Lyft',
                                'ABNB': 'Airbnb',
                                'DASH': 'DoorDash',
                                
                                # ========== E-COMMERCE & RETAIL ==========
                                'SHOP': 'Shopify',
                                'EBAY': 'eBay',
                                'ETSY': 'Etsy',
                                'WMT': 'Walmart',
                                'TGT': 'Target',
                                'COST': 'Costco',
                                'HD': 'Home Depot',
                                'LOW': "Lowe's",
                                'NKE': 'Nike',
                                
                                # ========== FINANCE & FINTECH ==========
                                'V': 'Visa',
                                'MA': 'Mastercard',
                                'PYPL': 'PayPal',
                                'SQ': 'Block',  # Formerly Square
                                'COIN': 'Coinbase',
                                'JPM': 'JPMorgan',
                                'BAC': 'Bank of America',
                                'WFC': 'Wells Fargo',
                                'GS': 'Goldman Sachs',
                                'MS': 'Morgan Stanley',
                                'AXP': 'American Express',
                                'C': 'Citigroup',
                                
                                # ========== HEALTHCARE & PHARMA ==========
                                'JNJ': 'Johnson & Johnson',
                                'UNH': 'UnitedHealth',
                                'PFE': 'Pfizer',
                                'ABBV': 'AbbVie',
                                'TMO': 'Thermo Fisher',
                                'ABT': 'Abbott',
                                'LLY': 'Eli Lilly',
                                'MRK': 'Merck',
                                'AMGN': 'Amgen',
                                'GILD': 'Gilead',
                                'BMY': 'Bristol Myers Squibb',
                                'CVS': 'CVS Health',
                                
                                # ========== AUTOMOTIVE ==========
                                'GM': 'General Motors',
                                'F': 'Ford',
                                'RIVN': 'Rivian',
                                'LCID': 'Lucid',
                                'NIO': 'Nio',
                                'XPEV': 'XPeng',
                                'LI': 'Li Auto',
                                
                                # ========== AEROSPACE & DEFENSE ==========
                                'BA': 'Boeing',
                                'LMT': 'Lockheed Martin',
                                'RTX': 'Raytheon',
                                'NOC': 'Northrop Grumman',
                                'GD': 'General Dynamics',
                                
                                # ========== ENERGY ==========
                                'XOM': 'ExxonMobil',
                                'CVX': 'Chevron',
                                'COP': 'ConocoPhillips',
                                'SLB': 'Schlumberger',
                                'OXY': 'Occidental',
                                'BP': 'BP',
                                'SHEL': 'Shell',
                                
                                # ========== CONSUMER GOODS ==========
                                'KO': 'Coca-Cola',
                                'PEP': 'PepsiCo',
                                'PG': 'Procter & Gamble',
                                'PM': 'Philip Morris',
                                'MO': 'Altria',
                                'MDLZ': 'Mondelez',
                                'CL': 'Colgate-Palmolive',
                                'KMB': 'Kimberly-Clark',
                                
                                # ========== INDUSTRIAL ==========
                                'CAT': 'Caterpillar',
                                'DE': 'Deere',
                                'MMM': '3M',
                                'HON': 'Honeywell',
                                'UPS': 'UPS',
                                'FDX': 'FedEx',
                                'GE': 'General Electric',
                                
                                # ========== TELECOM ==========
                                'T': 'AT&T',
                                'VZ': 'Verizon',
                                'TMUS': 'T-Mobile',
                                
                                # ========== SEMICONDUCTORS ==========
                                'MU': 'Micron',
                                'AMAT': 'Applied Materials',
                                'LRCX': 'Lam Research',
                                'KLAC': 'KLA',
                                'MRVL': 'Marvell',
                                'ON': 'ON Semiconductor',
                                
                                # ========== GAMING ==========
                                'EA': 'Electronic Arts',
                                'ATVI': 'Activision',  # Now part of MSFT
                                'TTWO': 'Take-Two',
                                'U': 'Unity',
                                
                                # ========== REAL ESTATE ==========
                                'AMT': 'American Tower',
                                'PLD': 'Prologis',
                                'CCI': 'Crown Castle',
                                'EQIX': 'Equinix',
                                
                                # ========== CRYPTO-RELATED ==========
                                'MSTR': 'MicroStrategy',
                                'MARA': 'Marathon Digital',
                                'RIOT': 'Riot Platforms',
                                
                                # ========== CHINESE STOCKS ==========
                                'BABA': 'Alibaba',
                                'JD': 'JD.com',
                                'PDD': 'Pinduoduo',
                                'BIDU': 'Baidu',
                                'BILI': 'Bilibili',
                                
                                # ========== MEME STOCKS / HIGH VOLATILITY ==========
                                'GME': 'GameStop',
                                'AMC': 'AMC Entertainment',
                                'BBBY': 'Bed Bath & Beyond',
                                'BB': 'BlackBerry',
                                
                                # ========== ETFS (Bonus) ==========
                                'SPY': 'S&P 500 ETF',
                                'QQQ': 'Nasdaq 100 ETF',
                                'DIA': 'Dow Jones ETF',
                                'IWM': 'Russell 2000 ETF',
                                'VOO': 'Vanguard S&P 500',
                                'VTI': 'Vanguard Total Market',
                            }

            
            # Use company name if available, otherwise use ticker
            search_query = company_map.get(stock_ticker.upper(), stock_ticker)
            
            logger.info(f"🔍 Scraping news for {search_query} ({stock_ticker})...")
            
            # Calculate date range (last 7 days)
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            # NewsAPI parameters
            params = {
                'q': f'{search_query} stock OR {search_query} earnings OR {search_query} shares',
                'apiKey': self.news_api_key,
                'language': 'en',
                'sortBy': 'relevancy',  # Most relevant first
                'from': from_date,
                'pageSize': min(max_results, 100)  # NewsAPI max is 100
            }
            
            # Make API request
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'ok':
                    for article in data.get('articles', []):
                        # Combine title and description for better sentiment analysis
                        title = article.get('title', '')
                        description = article.get('description', '')
                        content = article.get('content', '')
                        
                        # Create combined text (title + description gives best context)
                        text = f"{title} {description}"
                        
                        # Skip if text is too short or contains removal message
                        if len(text.strip()) < 20 or '[Removed]' in text:
                            continue
                        
                        articles.append({
                            'text': text,
                            'source': 'news',
                            'title': title,
                            'url': article.get('url', ''),
                            'publisher': article.get('source', {}).get('name', 'Unknown'),
                            'timestamp': datetime.strptime(
                                article.get('publishedAt', '').split('T')[0], 
                                '%Y-%m-%d'
                            ) if article.get('publishedAt') else datetime.now(),
                            'author': article.get('author', 'Unknown')
                        })
                    
                    logger.info(f"✅ Found {len(articles)} news articles about {search_query}")
                else:
                    logger.error(f"❌ NewsAPI returned error: {data.get('message', 'Unknown error')}")
            
            else:
                logger.error(f"❌ NewsAPI request failed with status {response.status_code}")
            
            return articles
        
        except Exception as e:
            logger.error(f"❌ News scraping error: {str(e)}")
            return []


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
