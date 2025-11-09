"""
Streamlit Web Application
Frontend for Stock Sentiment Advisor
"""

import streamlit as st
import logging
from datetime import datetime
from agent import StockAdvisorAgent
from notification import NotificationHandler
import json

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
    .main {
        padding-top: 0rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .buy-action {
        color: green;
        font-weight: bold;
        font-size: 24px;
    }
    .sell-action {
        color: red;
        font-weight: bold;
        font-size: 24px;
    }
    .hold-action {
        color: orange;
        font-weight: bold;
        font-size: 24px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = StockAdvisorAgent()

if 'notification_handler' not in st.session_state:
    st.session_state.notification_handler = NotificationHandler()

if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []


def main():
    # Header
    st.title("📊 AI Stock Sentiment Advisor")
    st.markdown("---")
    
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
        
        # Analyze button
        analyze_button = st.button("🔍 Analyze Stock", use_container_width=True)
        
        # Email notification
        st.markdown("---")
        st.subheader("📧 Email Notification")
        
        send_email = st.checkbox("Send recommendation to email")
        if send_email:
            recipient_email = st.text_input(
                "Recipient Email",
                placeholder="your-email@example.com",
                help="Email to send recommendation"
            )
        else:
            recipient_email = None
    
    # Main content area
    if analyze_button and stock_ticker:
        with st.spinner(f"🔄 Analyzing {stock_ticker}... This may take a minute..."):
            try:
                # Run agent analysis
                result = st.session_state.agent.execute(stock_ticker)
                
                # Extract recommendation
                recommendation = result['recommendation']
                
                # Store in history
                st.session_state.analysis_history.append(recommendation)
                
                # Display results
                st.markdown("---")
                st.subheader(f"Analysis Results for {stock_ticker}")
                
                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    action_color = (
                        "green" if recommendation['action'] == 'BUY' 
                        else "red" if recommendation['action'] == 'SELL' 
                        else "orange"
                    )
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
                    st.metric(
                        "Investment",
                        f"{recommendation['investment_percent']}%",
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
                    st.json(recommendation, expanded=False)
                
                # Send email if requested
                if send_email and recipient_email:
                    with st.spinner("📧 Sending email..."):
                        success = st.session_state.notification_handler.send_email_recommendation(
                            recommendation,
                            recipient_email
                        )
                        
                        if success:
                            st.success(f"✅ Email sent to {recipient_email}")
                        else:
                            st.error(f"❌ Failed to send email")
                
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
                with col2:
                    st.write(f"**Sentiment:** {record['sentiment_score']:.3f}")
                    st.write(f"**Investment:** {record['investment_percent']}%")
    else:
        st.info("No analysis history yet. Start by analyzing a stock!")


if __name__ == "__main__":
    main()
