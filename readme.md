Overview
Stock markets move not just on numbers, but on emotion.
Every tweet, Reddit thread, and headline reflects investor mood — bullish or bearish — and this sentiment often drives short-term volatility.
This model leverages the power of Machine Learning driven sentiment analysis to quantify this emotion.
 It continuously scrapes social media data (Twitter, Reddit and News API), performs hourly sentiment analysis, and converts the sentiment score into an actionable investment recommendation.
Our goal is to help traders and analysts see beyond prices and understand why the market feels the way it does, and how that feeling is likely to affect tomorrow’s prices.

How It Works
User Input 
The user begins by entering the name or ticker symbol of a company (e.g., Tesla or TSLA) into the app interface.
Data Collection


Tweets and Reddit posts mentioning a selected stock (e.g., TSLA, NVDA, AAPL) are fetched using official APIs and News API.


The agent gathers new data periodically to capture shifting market emotions.

Sentiment Analysis


Each post is cleaned, tokenized, and analyzed using an NLP sentiment model (Hugging Face / AWS Comprehend).
Model_Name = twitter-roberta-base-sentiment
The system assigns a continuous sentiment score between -1 and +1, where score near :
+1 is  very positive (strong buy sentiment)
0 is neutral
-1 is  very negative (strong sell sentiment)


Investment Decision Formula
 
SentimentScore = log(1+Negative_Count / 1+Positive_Count​)
InvestmentAmount = BaseBudget*(Tanh(SentimentScore)) 

 Tech Stack
Languages: Python
Data Handling: Pandas, NumPy
Streamlit - Used to build an interactive web app interface for displaying sentiment scores, stock trends, and predictions.
PRAW - Fetches Reddit posts and headlines for sentiment analysis.
Tweepy - Gathers tweets related to specific stocks or market trends
Python-dotenv - Loads API keys and credentials (like Reddit/Twitter keys) from a .env file securely.
Emoji - Handles or removes emojis in Reddit/Twitter text before sentiment analysis to avoid tokenization issues
Requests - Used to fetch data from external APIs (like financial or news APIs)
Transformers - Provides pretrained NLP models (like BERTweet) for generating sentiment scores between -1 and +1.
Torch - Backend deep learning framework that powers the transformer models.

Yfinance -displays a candlestick chart generated using data from Yahoo Finance
Plotly - Creates interactive graphs and visualizations (e.g., sentiment vs. stock price trends


Results
We observe the positive correlationship between public sentiment (derived from Reddit and Twitter posts) and the actual stock price movements over time.
We also verified that:
Positive spikes in sentiment often precede increase in price (buy signals).


Negative sentiment dips aligning with downward price trends (sell signals).

Challenges
During the development of News-Investment-Predictor, we faced several challenges. The first major hurdle was accessing high-quality, real-time data from platforms like Twitter and Reddit, as many APIs have rate limits or require elevated access. Moreover we were not able to integrate with AWS because we faced AccessError. Another challenge was handling noise in sentiment analysis — social media language is often sarcastic, informal, or context-dependent, making it difficult for models to interpret correctly.

Future Improvements
Use LSTM / Transformer models to forecast sentiment-driven price movement.
Differentiate between bot accounts and real accounts on twitter and reddit.


Add entity recognition to distinguish between company mentions (e.g., “Apple” vs “apple juice”).


Expand to multi-platform sentiment aggregation (YouTube, Financial Times, Bloomberg headlines).

