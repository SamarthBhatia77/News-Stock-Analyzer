"""
Agentic AI Module
Orchestrates the entire workflow: observe -> scrape -> clean -> predict -> act
"""

import os
import logging
import json
from datetime import datetime
from scrapers import UnifiedScraper
from text_cleaner import TextCleaner
from dotenv import load_dotenv
import numpy as np

# ML Model imports
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

load_dotenv()
logger = logging.getLogger(__name__)


class StockAdvisorAgent:
    def __init__(self):
        """Initialize the agentic AI agent"""
        self.scraper = UnifiedScraper()
        self.cleaner = TextCleaner()
        self.history = []
        logger.info("🤖 Stock Advisor Agent initialized")
    
    def observe(self, stock_ticker: str) -> dict:
        """
        STEP 1: OBSERVE
        Agent observes user request and decides what data to gather
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
        """
        logger.info(f"\n🧹 AGENT STEP 3 - CLEAN")
        
        raw_data = state['raw_data']
        logger.info(f"   Cleaning {len(raw_data)} texts...")
        
        cleaned_data = self.cleaner.clean_scraper_output(raw_data)
        cleaned_texts = [item['cleaned_text'] for item in cleaned_data 
                        if 'cleaned_text' in item and item['cleaned_text']]
        
        state['cleaned_data'] = cleaned_data
        state['cleaned_texts'] = cleaned_texts
        logger.info(f"   ✅ Cleaned {len(cleaned_texts)} texts")
        
        return state
    
    def predict(self, state: dict) -> dict:
        """
        STEP 4: PREDICT
        Agent runs sentiment analysis using RoBERTa
        """
        logger.info(f"\n🤖 AGENT STEP 4 - PREDICT")
        
        cleaned_texts = state['cleaned_texts']
        logger.info(f"   Running sentiment analysis on {len(cleaned_texts)} texts...")
        
        try:
            # Load model if not already loaded
            if not hasattr(self, 'tokenizer'):
                MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
                logger.info(f"   Loading model: {MODEL_NAME}")
                
                self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
                self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
                self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
                self.model.to(self.device)
                self.model.eval()
                
                logger.info(f"   ✅ Model loaded on device: {self.device}")
            
            # Batch prediction
            def predict_batch_scores(texts):
                enc = self.tokenizer(
                    texts, 
                    padding=True, 
                    truncation=True, 
                    max_length=256,
                    return_tensors='pt'
                )
                enc = {k: v.to(self.device) for k, v in enc.items()}
                
                with torch.no_grad():
                    out = self.model(**enc)
                    probs = F.softmax(out.logits, dim=-1).cpu().numpy()
                
                # Return probabilities: [negative, neutral, positive]
                return probs
            
            # Process in batches
            BATCH_SIZE = 32
            all_probs = []
            
            for i in range(0, len(cleaned_texts), BATCH_SIZE):
                batch = cleaned_texts[i:i + BATCH_SIZE]
                batch_probs = predict_batch_scores(batch)
                all_probs.extend(batch_probs)
            
            # Convert to numpy array
            all_probs = np.array(all_probs)
            
            # Calculate counts: probs[:, 0]=negative, probs[:, 2]=positive
            # Use probability > 0.5 as threshold for counting
            positive_count = np.sum(all_probs[:, 2] > 0.5)
            negative_count = np.sum(all_probs[:, 0] > 0.5)
            
            # NEW FORMULA: Sentiment Score = ln[(1 + Positive Count) / (1 + Negative Count)]
            sentiment_score = np.log((1 + positive_count) / (1 + negative_count))
            
            # Store individual scores for reference (old method)
            individual_scores = all_probs[:, 2] - all_probs[:, 0]
            
            state['sentiment_scores'] = individual_scores.tolist()
            state['sentiment_score'] = float(sentiment_score)
            state['positive_count'] = int(positive_count)
            state['negative_count'] = int(negative_count)
            
            logger.info(f"   ✅ Analyzed {len(cleaned_texts)} texts")
            logger.info(f"   Positive count: {positive_count}")
            logger.info(f"   Negative count: {negative_count}")
            logger.info(f"   Sentiment score: {sentiment_score:.4f}")
            
        except Exception as e:
            logger.error(f"   ❌ Error: {str(e)}")
            state['sentiment_score'] = 0.0
            state['sentiment_scores'] = []
            state['positive_count'] = 0
            state['negative_count'] = 0
        
        return state
    
    def act(self, state: dict, budget: float = 10000.0) -> dict:
        """
        STEP 5: ACT
        Agent interprets sentiment score and generates investment recommendation
        
        Uses formulas:
        - Sentiment Score = ln[(1 + Positive Count) / (1 + Negative Count)]
        - Investment Amount = Base Budget × tanh(Sentiment Score)
        """
        logger.info(f"\n⚡ AGENT STEP 5 - ACT")
        
        sentiment_score = state.get('sentiment_score', 0.0)
        stock_ticker = state['stock_ticker']
        positive_count = state.get('positive_count', 0)
        negative_count = state.get('negative_count', 0)
        
        logger.info(f"   Sentiment score: {sentiment_score:.4f}")
        logger.info(f"   Generating investment recommendation...")
        
        # NEW FORMULA: Investment Amount = Base Budget × tanh(Sentiment Score)
        tanh_value = np.tanh(sentiment_score)
        investment_amount = budget * tanh_value
        investment_percent = tanh_value * 100  # Convert to percentage
        
        # Determine action based on sentiment score thresholds
        if sentiment_score > 0.15:
            action = "BUY"
            confidence = min(abs(tanh_value), 1.0)
            reasoning = (
                f"Positive sentiment (score: {sentiment_score:.2f}, "
                f"{positive_count} positive vs {negative_count} negative mentions). "
                f"Market discussion leans optimistic about {stock_ticker}. "
                f"Consider buying."
            )
        
        elif sentiment_score < -0.15:
            action = "SELL"
            confidence = min(abs(tanh_value), 1.0)
            reasoning = (
                f"Negative sentiment (score: {sentiment_score:.2f}, "
                f"{positive_count} positive vs {negative_count} negative mentions). "
                f"Market discussion shows concerns about {stock_ticker}. "
                f"Consider selling or avoiding."
            )
        
        else:  # -0.15 to +0.15
            action = "HOLD"
            confidence = 0.5
            investment_amount = 0.0
            investment_percent = 0.0
            reasoning = (
                f"Neutral sentiment (score: {sentiment_score:.2f}, "
                f"{positive_count} positive vs {negative_count} negative mentions). "
                f"Market opinion is mixed about {stock_ticker}. "
                f"Wait for clearer signals."
            )
        
        recommendation = {
            'stock_ticker': stock_ticker,
            'action': action,
            'confidence': float(confidence),
            'sentiment_score': float(sentiment_score),
            'positive_count': int(positive_count),
            'negative_count': int(negative_count),
            'investment_percent': float(investment_percent),
            'investment_amount': float(investment_amount),
            'budget': float(budget),
            'reasoning': reasoning,
            'timestamp': state['timestamp'],
            'data_points': state['raw_data_count']
        }
        
        state['recommendation'] = recommendation
        
        logger.info(f"\n✅ RECOMMENDATION:")
        logger.info(f"   Action: {action}")
        logger.info(f"   Confidence: {confidence:.2%}")
        logger.info(f"   Investment: ${investment_amount:,.2f} ({investment_percent:.2f}%)")
        logger.info(f"   Reasoning: {reasoning}")
        
        recommendation = {
        'stock_ticker': stock_ticker,
        'action': action,
        'confidence': float(confidence),
        'sentiment_score': float(sentiment_score),
        'positive_count': int(positive_count),
        'negative_count': int(negative_count),
        'investment_percent': float(investment_percent),
        'investment_amount': float(investment_amount),
        'budget': float(budget),
        'reasoning': reasoning,
        'timestamp': state['timestamp'],
        'data_points': state['raw_data_count']
    }
    
        # NEW: Add source references (max 10 from each source)
        raw_data = state.get('raw_data', [])
        
        # Separate by source
        reddit_sources = [item for item in raw_data if item.get('source') == 'reddit']
        twitter_sources = [item for item in raw_data if item.get('source') == 'twitter']
        news_sources = [item for item in raw_data if item.get('source') in ['newsapi', 'google_news']]
        
        # Take up to 10 from each
        recommendation['references'] = {
            'reddit': reddit_sources[:min(10, len(reddit_sources))],
            'twitter': twitter_sources[:min(10, len(twitter_sources))],
            'news': news_sources[:min(10, len(news_sources))]
        }
        
        state['recommendation'] = recommendation
        
        logger.info(f"\n✅ RECOMMENDATION:")
        logger.info(f"   Action: {action}")
        logger.info(f"   Confidence: {confidence:.2%}")
        logger.info(f"   Investment: ${investment_amount:,.2f} ({investment_percent:.2f}%)")
        logger.info(f"   Reasoning: {reasoning}")

        return state
    
    def execute(self, stock_ticker: str, budget: float = 10000.0) -> dict:
        """
        Main execution method - runs complete agent loop
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
        state = self.act(state, budget=budget)
        
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
    result = agent.execute("AAPL", budget=10000)
    print(json.dumps(result['recommendation'], indent=2, default=str))
