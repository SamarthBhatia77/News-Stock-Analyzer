import requests
from scrapers import scrape_all_sources
from text_cleaner import clean_multiple_texts
import os
from dotenv import load_dotenv

load_dotenv()

COLAB_MODEL_URL = os.getenv('COLAB_MODEL_URL')

class StockAdvisorAgent:
    """
    Agentic AI that orchestrates the entire stock analysis workflow
    """
    
    def __init__(self):
        self.colab_model_url = COLAB_MODEL_URL
    
    def extract_stock_info(self, user_query):
        """
        Extracts company name and stock symbol from user query
        For simplicity, using a mapping. You can use LLM for this.
        """
        # Simple keyword matching (you can make this smarter with LLM)
        stock_map = {
            'apple': ('Apple', 'AAPL'),
            'nvidia': ('NVIDIA', 'NVDA'),
            'tesla': ('Tesla', 'TSLA'),
            'microsoft': ('Microsoft', 'MSFT'),
            'amazon': ('Amazon', 'AMZN'),
            'google': ('Google', 'GOOGL'),
            'meta': ('Meta', 'META'),
        }
        
        query_lower = user_query.lower()
        
        for keyword, (company, symbol) in stock_map.items():
            if keyword in query_lower:
                return company, symbol
        
        return None, None
    
    def scrape_social_media(self, stock_symbol, company_name):
        """
        Step 2: Scrape Reddit and Twitter
        """
        return scrape_all_sources(stock_symbol, company_name)
    
    def clean_texts(self, raw_texts):
        """
        Step 3: Clean scraped texts
        """
        print(f"\n[2/5] Cleaning {len(raw_texts)} texts...")
        cleaned = clean_multiple_texts(raw_texts)
        print(f"✓ {len(cleaned)} texts cleaned (removed {len(raw_texts) - len(cleaned)} invalid)")
        return cleaned
    
    def get_sentiment_scores(self, clean_texts):
        """
        Step 4: Send to Google Colab model for sentiment analysis
        """
        print(f"\n[3/5] Sending texts to sentiment model...")
        
        try:
            response = requests.post(
                self.colab_model_url,
                json={'texts': clean_texts},
                timeout=60
            )
            
            result = response.json()
            scores = result['scores']  # List of scores from -1 to +1
            
            print(f"✓ Received {len(scores)} sentiment scores from model")
            return scores
            
        except Exception as e:
            print(f"✗ Error calling model: {str(e)}")
            return None
    
    def calculate_investment_recommendation(self, scores, stock_symbol):
        """
        Step 5: Calculate investment recommendation based on scores
        """
        print(f"\n[4/5] Calculating investment recommendation...")
        
        if not scores:
            return None
        
        # Calculate average sentiment score
        avg_score = sum(scores) / len(scores)
        
        # Count positive vs negative
        positive_count = sum(1 for s in scores if s > 0)
        negative_count = sum(1 for s in scores if s < 0)
        neutral_count = sum(1 for s in scores if s == 0)
        
        # Determine investment amount based on sentiment
        # This is where your model's investment calculation would go
        if avg_score >= 0.5:
            action = "STRONG BUY"
            investment_amount = 1000
            reasoning = "Very positive sentiment detected"
        elif avg_score >= 0.2:
            action = "BUY"
            investment_amount = 500
            reasoning = "Moderately positive sentiment"
        elif avg_score >= -0.2:
            action = "HOLD"
            investment_amount = 0
            reasoning = "Neutral sentiment - wait for clearer signals"
        elif avg_score >= -0.5:
            action = "CONSIDER SELLING"
            investment_amount = -300
            reasoning = "Moderately negative sentiment"
        else:
            action = "STRONG SELL"
            investment_amount = -500
            reasoning = "Very negative sentiment detected"
        
        recommendation = {
            'stock_symbol': stock_symbol,
            'average_score': round(avg_score, 3),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_analyzed': len(scores),
            'action': action,
            'investment_amount': investment_amount,
            'reasoning': reasoning,
            'confidence': abs(avg_score) * 100  # 0-100%
        }
        
        print(f"✓ Recommendation: {action} ${abs(investment_amount)}")
        return recommendation
    
    def analyze_stock(self, user_query):
        """
        Main agent workflow - orchestrates all steps
        """
        print("="*60)
        print("AGENTIC AI STOCK ADVISOR - ANALYSIS STARTING")
        print("="*60)
        
        # Step 1: Extract stock info from query
        company_name, stock_symbol = self.extract_stock_info(user_query)
        
        if not company_name:
            return {
                'error': 'Could not identify stock from query. Try mentioning a company name.'
            }
        
        print(f"\n[0/5] Analyzing: {company_name} ({stock_symbol})")
        
        # Step 2: Scrape social media
        raw_texts = self.scrape_social_media(stock_symbol, company_name)
        
        if not raw_texts:
            return {
                'error': 'No social media data found for this stock'
            }
        
        # Step 3: Clean texts
        clean_texts = self.clean_texts(raw_texts)
        
        # Step 4: Get sentiment scores from your model
        scores = self.get_sentiment_scores(clean_texts)
        
        if not scores:
            return {
                'error': 'Failed to get sentiment scores from model'
            }
        
        # Step 5: Calculate recommendation
        recommendation = self.calculate_investment_recommendation(scores, stock_symbol)
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60 + "\n")
        
        return recommendation
