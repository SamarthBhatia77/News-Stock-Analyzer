"""
Streamlit Web Application
Frontend for Stock Sentiment Advisor
"""

import streamlit as st
import logging
from datetime import datetime
from agent import StockAdvisorAgent
import json
import yfinance as yf
import plotly.graph_objects as go
from datetime import timedelta
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Stock Sentiment Advisor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = StockAdvisorAgent()
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []


def get_stock_price_chart(ticker: str, period: str = "6mo"):
    """
    Fetch and create stock price chart using yfinance
    """
    try:
        # Download stock data
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            return None
        
        # Create candlestick chart
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name='Price'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'{ticker} Stock Price ({period})',
            yaxis_title='Price (USD)',
            xaxis_title='Date',
            template='plotly_dark',
            height=400,
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error fetching stock data: {e}")
        return None


def calculate_investment_amount(sentiment_score: float, budget: float) -> float:
    """
    Calculate investment amount using tanh function
    Maps sentiment (-1 to +1) to investment amount
    """
    # Use tanh to map sentiment to 0-1 range smoothly
    # tanh(2x) provides good sensitivity around 0
    normalized = np.tanh(2 * sentiment_score)
    
    # Map to percentage of budget (0% to 100%)
    # Only invest on positive sentiment
    if normalized > 0:
        investment_percent = (normalized * 100)  # 0% to 100%
        investment_amount = (investment_percent / 100) * budget
        return investment_amount, investment_percent
    else:
        return 0.0, 0.0


def format_recommendation_text(recommendation: dict) -> str:
    """
    Format recommendation dict as readable text
    """
    lines = []
    lines.append(f"Stock Ticker: {recommendation.get('stock_ticker', 'N/A')}")
    lines.append(f"Action: {recommendation.get('action', 'N/A')}")
    lines.append(f"Confidence: {recommendation.get('confidence', 0):.1%}")
    lines.append(f"Sentiment Score: {recommendation.get('sentiment_score', 0):.4f}")
    
    if 'investment_amount' in recommendation:
        lines.append(f"Investment Amount: ${recommendation.get('investment_amount', 0):,.2f}")
        lines.append(f"Investment Percentage: {recommendation.get('investment_percent', 0):.2f}%")
    else:
        lines.append(f"Investment Percentage: {recommendation.get('investment_percent', 0)}%")
    
    lines.append(f"Data Points Analyzed: {recommendation.get('data_points', 0)}")
    lines.append(f"Timestamp: {recommendation.get('timestamp', 'N/A')}")
    lines.append(f"\nReasoning: {recommendation.get('reasoning', 'N/A')}")
    
    return "\n".join(lines)

def generate_analysis_summary(recommendation: dict, stock_ticker: str) -> str:
    """
    Generate a comprehensive summary based on the recommendation
    """
    action = recommendation['action']
    confidence = recommendation['confidence']
    sentiment_score = recommendation['sentiment_score']
    investment_amount = recommendation.get('investment_amount', 0)
    investment_percent = recommendation.get('investment_percent', 0)
    positive_count = recommendation.get('positive_count', 0)
    negative_count = recommendation.get('negative_count', 0)
    data_points = recommendation.get('data_points', 0)
    
    summary_lines = []
    
    # Opening statement
    summary_lines.append(f"## 📋 Analysis Summary for {stock_ticker}")
    summary_lines.append("")
    
    # Key findings
    summary_lines.append("### Key Findings")
    summary_lines.append(f"- **Market Sentiment:** {'Positive' if sentiment_score > 0.15 else 'Negative' if sentiment_score < -0.15 else 'Neutral'}")
    summary_lines.append(f"- **Confidence Level:** {confidence:.0%}")
    summary_lines.append(f"- **Data Coverage:** Analyzed {data_points} sources ({positive_count} positive, {negative_count} negative)")
    summary_lines.append("")
    
    # Recommendation interpretation
    summary_lines.append("### Our Understanding")
    
    if action == "BUY":
        summary_lines.append(
            f"The analysis suggests a **{action}** action with {confidence:.0%} confidence. "
            f"Based on {data_points} social media posts and news articles, there is a clear positive "
            f"sentiment toward {stock_ticker}. The sentiment score of {sentiment_score:.2f} indicates "
            f"that market discussion is leaning optimistic."
        )
        summary_lines.append("")
        summary_lines.append(
            f"**Investment Recommendation:** Consider allocating ${investment_amount:,.2f} "
            f"({investment_percent:.1f}% of your ${recommendation['budget']:,.0f} budget) to {stock_ticker}. "
            f"This allocation is based on the tanh-scaled sentiment score, which provides a balanced "
            f"approach to portfolio management."
        )
        
    elif action == "SELL":
        summary_lines.append(
            f"The analysis suggests a **{action}** action with {confidence:.0%} confidence. "
            f"Based on {data_points} sources, there is notable negative sentiment surrounding {stock_ticker}. "
            f"The sentiment score of {sentiment_score:.2f} indicates concerns in market discussion."
        )
        summary_lines.append("")
        summary_lines.append(
            f"**Risk Alert:** The negative sentiment suggests caution. Consider reducing exposure "
            f"or avoiding new positions in {stock_ticker} until sentiment improves."
        )
        
    else:  # HOLD
        summary_lines.append(
            f"The analysis suggests a **{action}** action. Based on {data_points} sources, "
            f"the sentiment is mixed with no clear direction. The sentiment score of {sentiment_score:.2f} "
            f"falls within the neutral range (-0.15 to +0.15)."
        )
        summary_lines.append("")
        summary_lines.append(
            f"**Recommendation:** Wait for clearer market signals before making investment decisions. "
            f"Monitor the stock for emerging trends in sentiment."
        )
    
    summary_lines.append("")
    summary_lines.append("### Important Disclaimer")
    summary_lines.append(
        "*This analysis is based purely on social media and news sentiment. It should be used as a "
        "complementary tool alongside fundamental analysis, technical indicators, and professional "
        "financial advice. Past sentiment does not guarantee future performance.*"
    )
    
    return "\n".join(summary_lines)


def format_source_reference(source_item: dict, index: int) -> str:
    """
    Format a single source reference with summary
    """
    text = source_item.get('text', '')
    url = source_item.get('url', '#')
    source_type = source_item.get('source', 'unknown')
    
    # Generate one-sentence summary (first 150 characters)
    summary = text[:150] + "..." if len(text) > 150 else text
    
    # Format based on source type
    if source_type == 'reddit':
        title = source_item.get('title', 'Reddit Post')
        return f"{index}. **[Reddit]** [{title}]({url})  \n   *Summary:* {summary}"
    elif source_type == 'twitter':
        return f"{index}. **[Twitter]** [Tweet Link]({url})  \n   *Summary:* {summary}"
    elif source_type in ['newsapi', 'google_news']:
        title = source_item.get('title', 'News Article')
        publisher = source_item.get('publisher', 'Unknown')
        return f"{index}. **[{publisher}]** [{title}]({url})  \n   *Summary:* {summary}"
    else:
        return f"{index}. **[Source]** [Link]({url})  \n   *Summary:* {summary}"


def main():
    # Header
    st.title("📊 AI Stock Sentiment Advisor")
    #st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Stock input
        stock_ticker = st.text_input(
            "Enter Stock Ticker",
            value="AAPL",
            placeholder="e.g., AAPL, TSLA, GOOGL",
            help="Stock symbol to analyze"
        ).upper()
        
        # Investment budget input
        investment_budget = st.number_input(
            "Investment Budget ($)",
            min_value=100.0,
            max_value=1000000.0,
            value=10000.0,
            step=100.0,
            help="Total amount you want to consider for investment"
        )
        
        # Analyze button
        analyze_button = st.button("🔍 Analyze Stock", use_container_width=True)
    
    # Main content area
    if analyze_button and stock_ticker:
        with st.spinner(f"🔄 Analyzing {stock_ticker}... This may take a minute..."):
            try:
                # Run agent analysis
                result = st.session_state.agent.execute(stock_ticker, budget=investment_budget)
                
                # Extract recommendation
                recommendation = result['recommendation']
                
                # Store in history
                st.session_state.analysis_history.append(recommendation)
                
                # Display stock price chart
                st.markdown("---")
                st.subheader(f"📈 {stock_ticker} Price Chart")
                
                chart = get_stock_price_chart(stock_ticker, period="1mo")
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
                else:
                    st.warning("⚠️ Could not fetch stock price data")
                
                # Display results
                st.markdown("---")
                st.subheader(f"Analysis Results for {stock_ticker}")
                
                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Action",
                        recommendation['action'],
                        delta=f"{recommendation['confidence']:.0%} confidence"
                    )
                
                with col2:
                    st.metric(
                        "Sentiment Score",
                        f"{recommendation['sentiment_score']:.3f}",
                        delta="Scale: -1 to +1"
                    )
                
                with col3:
                    if 'investment_amount' in recommendation:
                        st.metric(
                            "Investment",
                            f"${recommendation['investment_amount']:,.2f}",
                            delta=f"{recommendation['investment_percent']:.1f}% of budget"
                        )
                    else:
                        st.metric(
                            "Investment",
                            f"{recommendation.get('investment_percent', 0)}%",
                            delta="of your portfolio"
                        )
                
                with col4:
                    st.metric(
                        "Data Points",
                        recommendation['data_points'],
                        delta="sources analyzed"
                    )
                
                # Detailed reasoning
                st.markdown("---")
                st.subheader("💡 Analysis Details")
                
                with st.expander("📝 Detailed Reasoning"):
                    st.write(recommendation['reasoning'])
                
                with st.expander("📊 Raw Recommendation"):
                    # Display as formatted text instead of JSON
                    st.text(format_recommendation_text(recommendation))
                
                # NEW: Add References Section
                # NEW: Add References Section
                if 'references' in recommendation:
                    st.markdown("---")
                    st.subheader("🔗 Source References")
                    
                    references = recommendation['references']
                    
                    # Check if any references exist
                    has_reddit = references.get('reddit') and len(references['reddit']) > 0
                    has_twitter = references.get('twitter') and len(references['twitter']) > 0
                    has_news = references.get('news') and len(references['news']) > 0
                    
                    # If no references at all, show message
                    if not (has_reddit or has_twitter or has_news):
                        st.warning("⚠️ No references found. The analysis used very limited data sources and may be unreliable.")
                    else:
                        # Only show sections that have data
                        if has_reddit:
                            with st.expander(f"📱 Reddit Posts ({len(references['reddit'])} sources)"):
                                for idx, item in enumerate(references['reddit'], 1):
                                    st.markdown(format_source_reference(item, idx))
                                    if idx < len(references['reddit']):
                                        st.markdown("---")
                        
                        if has_twitter:
                            with st.expander(f"🐦 Twitter Posts ({len(references['twitter'])} sources)"):
                                for idx, item in enumerate(references['twitter'], 1):
                                    st.markdown(format_source_reference(item, idx))
                                    if idx < len(references['twitter']):
                                        st.markdown("---")
                        
                        if has_news:
                            with st.expander(f"📰 News Articles ({len(references['news'])} sources)"):
                                for idx, item in enumerate(references['news'], 1):
                                    st.markdown(format_source_reference(item, idx))
                                    if idx < len(references['news']):
                                        st.markdown("---")


                # NEW: Add Summary Section
                st.markdown("---")
                st.subheader("🎯 Understanding the Analysis")

                with st.expander("📝 Comprehensive Summary", expanded=True):
                    summary = generate_analysis_summary(recommendation, stock_ticker)
                    st.markdown(summary)
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                logger.error(f"Error: {str(e)}")
    
    # History section
    st.markdown("---")
    st.subheader("📜 Analysis History")
    
    if st.session_state.analysis_history:
        for idx, record in enumerate(reversed(st.session_state.analysis_history)):
            with st.expander(
                f"{record['stock_ticker']} - {record['action']} - {record['timestamp']}"
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Action:** {record['action']}")
                    st.write(f"**Confidence:** {record['confidence']:.0%}")
                    st.write(f"**Sentiment:** {record['sentiment_score']:.3f}")
                
                with col2:
                    if 'investment_amount' in record:
                        st.write(f"**Investment Amount:** ${record['investment_amount']:,.2f}")
                        st.write(f"**Investment %:** {record['investment_percent']:.2f}%")
                    else:
                        st.write(f"**Investment:** {record.get('investment_percent', 0)}%")
                    st.write(f"**Data Points:** {record.get('data_points', 0)}")
    else:
        st.info("No analysis history yet. Start by analyzing a stock!")


if __name__ == "__main__":
    main()
