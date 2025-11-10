# News-Investment-Predictor

## Overview
Stock markets move not just on numbers, but on emotion. Every tweet, Reddit thread, and headline reflects investor mood — bullish or bearish — and this sentiment often drives short-term volatility. This model leverages the power of Machine Learning driven sentiment analysis to quantify this emotion. It continuously scrapes social media data (Twitter, Reddit and News API), performs hourly sentiment analysis, and converts the sentiment score into an actionable investment recommendation. Our goal is to help traders and analysts see beyond prices and understand why the market feels the way it does, and how that feeling is likely to affect tomorrow's prices.

## How It Works

### User Input
The user begins by entering the name or ticker symbol of a company (e.g., Tesla or TSLA) into the app interface.

### Data Collection
- Tweets and Reddit posts mentioning a selected stock (e.g., TSLA, NVDA, AAPL) are fetched using official APIs and News API.
- The agent gathers new data periodically to capture shifting market emotions.

### Sentiment Analysis
- Each post is cleaned, tokenized, and analyzed using an NLP sentiment model (Hugging Face / AWS Comprehend).
- **Model Name:** `twitter-roberta-base-sentiment`
- The system assigns a continuous sentiment score between -1 and +1, where:
  - **+1** is very positive (strong buy sentiment)
  - **0** is neutral
  - **-1** is very negative (strong sell sentiment)

### Investment Decision Formula:
$$
(i) \mathrm{SentimentScore} = \log\left(\frac{1 + \mathrm{Negative\_Count}}{1 + \mathrm{Positive\_Count}}\right)
$$

$$
(ii) \mathrm{InvestmentAmount} = \mathrm{BaseBudget} \times \tanh(\mathrm{SentimentScore})
$$


## Tech Stack

### Languages
Python

### Libraries and Frameworks
- **Pandas, NumPy** - Data handling
- **Streamlit** - Interactive web app interface for displaying sentiment scores, stock trends, and predictions
- **PRAW** - Fetches Reddit posts and headlines for sentiment analysis
- **Tweepy** - Gathers tweets related to specific stocks or market trends
- **Python-dotenv** - Loads API keys and credentials securely from `.env` file
- **Emoji** - Handles or removes emojis in Reddit/Twitter text before sentiment analysis
- **Requests** - Fetches data from external APIs (financial or news APIs)
- **Transformers** - Provides pretrained NLP models (like BERTweet) for sentiment score generation
- **Torch** - Backend deep learning framework that powers the transformer models
- **Yfinance** - Displays candlestick charts using Yahoo Finance data
- **Plotly** - Creates interactive graphs and visualizations (e.g., sentiment vs. stock price trends)

## Results
We observe positive correlation between public sentiment (derived from Reddit and Twitter posts) and actual stock price movements over time. We verified that:
- Positive spikes in sentiment often precede increases in price (buy signals)
- Negative sentiment dips align with downward price trends (sell signals)

## Challenges
During development, we faced several challenges. The first major hurdle was accessing high-quality, real-time data from platforms like Twitter and Reddit, as many APIs have rate limits or require elevated access. We were not able to integrate with AWS because we faced AccessError. Another challenge was handling noise in sentiment analysis — social media language is often sarcastic, informal, or context-dependent, making it difficult for models to interpret correctly.

## Future Improvements
- Use LSTM / Transformer models to forecast sentiment-driven price movement
- Differentiate between bot accounts and real accounts on Twitter and Reddit
- Add entity recognition to distinguish between company mentions (e.g., "Apple" vs "apple juice")
- Expand to multi-platform sentiment aggregation (YouTube, Financial Times, Bloomberg headlines)






