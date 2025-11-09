import streamlit as st
from agent import StockAdvisorAgent
from notification import send_email_notification

# Page configuration
st.set_page_config(
    page_title="AI Stock Advisor",
    page_icon="📈",
    layout="wide"
)

# Initialize agent
if 'agent' not in st.session_state:
    st.session_state.agent = StockAdvisorAgent()

# Title
st.title("📈 AI Stock Investment Advisor")
st.markdown("*Powered by Agentic AI & Sentiment Analysis*")

# Sidebar for user settings
st.sidebar.header("📧 Email Settings")
user_email = st.sidebar.text_input(
    "Your Email Address",
    placeholder="your@email.com",
    help="Enter email to receive stock recommendations"
)


# Main input
st.markdown("---")
user_query = st.text_input(
    "🔍 What stock would you like to analyze?",
    placeholder="E.g., Please analyze stocks of Apple for me",
    help="Enter a company name like Apple, Tesla, NVIDIA, etc."
)

analyze_button = st.button("🚀 Analyze Stock", type="primary", use_container_width=True)

# Analysis logic
if analyze_button and user_query:
    
    with st.spinner("🤖 Agent working... This may take 30-60 seconds"):
        # Run the agent
        result = st.session_state.agent.analyze_stock(user_query)
    
    if 'error' in result:
        st.error(f"❌ {result['error']}")
    
    else:
        # Display results
        st.success("✅ Analysis Complete!")
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Stock", result['stock_symbol'])
        
        with col2:
            st.metric("Action", result['action'])
        
        with col3:
            amount = result['investment_amount']
            st.metric("Amount", f"${abs(amount)}", 
                     delta=f"{'Invest' if amount > 0 else 'Sell'}")
        
        with col4:
            st.metric("Confidence", f"{result['confidence']:.1f}%")
        
        # Detailed breakdown
        st.markdown("---")
        st.subheader("📊 Sentiment Analysis Details")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write(f"**Average Sentiment Score:** {result['average_score']}")
            st.write(f"**Reasoning:** {result['reasoning']}")
            st.write(f"**Total Texts Analyzed:** {result['total_analyzed']}")
        
        with col_b:
            # Sentiment breakdown chart
            import pandas as pd
            sentiment_data = pd.DataFrame({
                'Sentiment': ['Positive', 'Negative', 'Neutral'],
                'Count': [
                    result['positive_count'],
                    result['negative_count'],
                    result['neutral_count']
                ]
            })
            st.bar_chart(sentiment_data.set_index('Sentiment'))
        
        # Recommendation box
        st.markdown("---")
        
        if result['investment_amount'] > 0:
            st.success(f"### 💰 Recommendation: {result['action']}")
            st.write(f"Consider investing **${result['investment_amount']}** in {result['stock_symbol']}")
        elif result['investment_amount'] < 0:
            st.warning(f"### ⚠️ Recommendation: {result['action']}")
            st.write(f"Consider selling **${abs(result['investment_amount'])}** worth of {result['stock_symbol']}")
        else:
            st.info(f"### 🤔 Recommendation: {result['action']}")
            st.write("Hold your position and wait for clearer signals")
        
        # Send email notification
        st.markdown("---")
        st.subheader("📧 Send Recommendation to Email")

        if st.button("📧 Send Email", type="primary", use_container_width=True):
            if user_email:
                with st.spinner("Sending email..."):
                    if send_email_notification(result, user_email):
                        st.success(f"✅ Email sent successfully to {user_email}")
                    else:
                        st.error("❌ Failed to send email. Check your Gmail settings.")
            else:
                st.warning("⚠️ Please enter your email address in the sidebar first")


# Footer
st.markdown("---")
st.caption("⚠️ This is not financial advice. Always conduct your own research before investing.")
