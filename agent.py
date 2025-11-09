"""
Agentic AI Module
Orchestrates the entire workflow: observe -> scrape -> clean -> predict -> act
"""

import os
import logging
from datetime import datetime
from scrapers import UnifiedScraper
from text_cleaner import TextCleaner
import requests
import json

load_dotenv()
logger = logging.getLogger(__name__)


class StockAdvisorAgent:
    def __init__(self):
        """Initialize the agentic AI agent"""
        self.scraper = UnifiedScraper()
        self.cleaner = TextCleaner()
        self.model_url = os.getenv('COLAB_MODEL_URL', 'http://localhost:5000/predict')
        self.history = []
        logger.info("🤖 Stock Advisor Agent initialized")
    
    def observe(self, stock_ticker: str) -> dict:
        """
        STEP 1: OBSERVE
        Agent observes user request and decides what data to gather
        
        Args:
            stock_ticker: Stock symbol to analyze
        
        Returns:
            State dict with observation results
        """
        logger.info(f"\n🔍 AGENT STEP 1 - OBSERVE")
        logger.info(f"   Stock ticker: {stock_ticker}")
        logger.info(f"   Decision: Need to scrape Reddit, Twitter, and News")
        
        state = {
            'stock_ticker': stock_ticker.upper(),
            'timestamp': datetime.now(),
            'status': 'observing'
        }
        
        return state
    
    def scrape(self, state: dict) -> dict:
        """
        STEP 2: SCRAPE
        Agent scrapes data from multiple sources
        
        Args:
            state: Current state dict
        
        Returns:
            Updated state with raw data
        """
        logger.info(f"\n📡 AGENT STEP 2 - SCRAPE")
        
        stock_ticker = state['stock_ticker']
        logger.info(f"   Scraping Reddit, Twitter, News for {stock_ticker}...")
        
        raw_data = self.scraper.scrape_all(
            stock_ticker,
            reddit_limit=30,
            twitter_limit=50,
            news_limit=20
        )
        
        state['raw_data'] = raw_data
        state['raw_data_count'] = len(raw_data)
        logger.info(f"   ✅ Collected {len(raw_data)} data points")
        
        return state
    
    def clean(self, state: dict) -> dict:
        """
        STEP 3: CLEAN
        Agent cleans data for ML model input
        
        Args:
            state: Current state dict
        
        Returns:
            Updated state with cleaned data
        """
        logger.info(f"\n🧹 AGENT STEP 3 - CLEAN")
        
        raw_data = state['raw_data']
        logger.info(f"   Cleaning {len(raw_data)} texts...")
        
        cleaned_data = self.cleaner.clean_scraper_output(raw_data)
        
        # Extract just the cleaned texts for ML model
        cleaned_texts = [item['cleaned_text'] for item in cleaned_data if 'cleaned_text' in item]
        
        state['cleaned_data'] = cleaned_data
        state['cleaned_texts'] = cleaned_texts
        logger.info(f"   ✅ Cleaned {len(cleaned_texts)} texts")
        
        return state
    
    def predict(self, state: dict) -> dict:
        """
        STEP 4: PREDICT
        Agent sends cleaned data to ML model and gets sentiment scores
        
        Args:
            state: Current state dict
        
        Returns:
            Updated state with predictions
        """
        logger.info(f"\n🤖 AGENT STEP 4 - PREDICT")
        
        cleaned_texts = state['cleaned_texts']
        logger.info(f"   Sending {len(cleaned_texts)} texts to ML model...")
        logger.info(f"   Model URL: {self.model_url}")
        
        try:
            # TODO: Replace with actual model endpoint
            # This assumes your friend's Google Colab provides a /predict endpoint
            # that accepts {'texts': [...]} and returns {'scores': [...]}
            
            response = requests.post(
                self.model_url,
                json={'texts': cleaned_texts},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                scores = result.get('scores', [])
                
                # Calculate average sentiment
                avg_sentiment = sum(scores) / len(scores) if scores else 0.0
                
                state['sentiment_scores'] = scores
                state['average_sentiment'] = avg_sentiment
                
                logger.info(f"   ✅ Got {len(scores)} sentiment scores")
                logger.info(f"   Average sentiment: {avg_sentiment:.4f}")
                
            else:
                logger.error(f"   ❌ Model error: {response.status_code}")
                state['average_sentiment'] = 0.0
                state['sentiment_scores'] = []
        
        except Exception as e:
            logger.error(f"   ❌ Error calling model: {str(e)}")
            state['average_sentiment'] = 0.0
            state['sentiment_scores'] = []
        
        return state
    
    def act(self, state: dict) -> dict:
        """
        STEP 5: ACT
        Agent interprets sentiment scores and generates investment recommendation
        
        Args:
            state: Current state dict
        
        Returns:
            Updated state with recommendation
        """
        logger.info(f"\n⚡ AGENT STEP 5 - ACT")
        
        sentiment = state.get('average_sentiment', 0.0)
        stock_ticker = state['stock_ticker']
        
        logger.info(f"   Sentiment score: {sentiment:.4f}")
        logger.info(f"   Generating investment recommendation...")
        
        # Agent reasoning logic
        if sentiment > 0.5:
            action = "BUY"
            confidence = min(sentiment, 1.0)
            investment_percent = int((sentiment - 0.5) * 40)  # Max 20% for score of 1.0
            reasoning = (
                f"Strong positive sentiment ({sentiment:.2f}). "
                f"Market discussion is overwhelmingly optimistic about {stock_ticker}. "
                f"Consider buying."
            )
        
        elif sentiment < -0.5:
            action = "SELL"
            confidence = min(abs(sentiment), 1.0)
            investment_percent = int((abs(sentiment) - 0.5) * 40)
            reasoning = (
                f"Strong negative sentiment ({sentiment:.2f}). "
                f"Market discussion shows concerns about {stock_ticker}. "
                f"Consider selling."
            )
        
        else:
            action = "HOLD"
            confidence = 0.5
            investment_percent = 0
            reasoning = (
                f"Neutral sentiment ({sentiment:.2f}). "
                f"Market opinion is mixed about {stock_ticker}. "
                f"Wait for clearer signals."
            )
        
        recommendation = {
            'stock_ticker': stock_ticker,
            'action': action,
            'confidence': float(confidence),
            'sentiment_score': float(sentiment),
            'investment_percent': investment_percent,
            'reasoning': reasoning,
            'timestamp': state['timestamp'],
            'data_points': state['raw_data_count']
        }
        
        state['recommendation'] = recommendation
        
        logger.info(f"\n✅ RECOMMENDATION:")
        logger.info(f"   Action: {action}")
        logger.info(f"   Confidence: {confidence:.2%}")
        logger.info(f"   Investment: {investment_percent}% of portfolio")
        logger.info(f"   Reasoning: {reasoning}")
        
        return state
    
    def execute(self, stock_ticker: str) -> dict:
        """
        Main execution method - runs complete agent loop
        
        OBSERVE → SCRAPE → CLEAN → PREDICT → ACT
        
        Args:
            stock_ticker: Stock to analyze
        
        Returns:
            Final state dict with recommendation
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 STOCK ADVISOR AGENT EXECUTION START")
        logger.info(f"{'='*60}")
        
        # Step 1: Observe
        state = self.observe(stock_ticker)
        
        # Step 2: Scrape
        state = self.scrape(state)
        
        if len(state['raw_data']) == 0:
            logger.warning(f"⚠️  No data found for {stock_ticker}")
            state['recommendation'] = {
                'stock_ticker': stock_ticker,
                'action': 'ERROR',
                'reasoning': 'No data found for this stock'
            }
            return state
        
        # Step 3: Clean
        state = self.clean(state)
        
        # Step 4: Predict
        state = self.predict(state)
        
        # Step 5: Act
        state = self.act(state)
        
        # Store in history
        self.history.append(state['recommendation'])
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ EXECUTION COMPLETE")
        logger.info(f"{'='*60}\n")
        
        return state
    
    def get_history(self) -> list:
        """Get historical recommendations"""
        return self.history


# Test the agent
if __name__ == "__main__":
    from dotenv import load_dotenv
    
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    agent = StockAdvisorAgent()
    result = agent.execute("AAPL")
    print(json.dumps(result['recommendation'], indent=2, default=str))
