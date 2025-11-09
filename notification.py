import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_email_notification(recommendation, recipient_email):
    """
    Sends investment recommendation via email using Gmail
    """
    sender_email = os.getenv('GMAIL_ADDRESS')
    sender_password = os.getenv('GMAIL_APP_PASSWORD')
    
    # Create email subject
    subject = f"📊 Stock Alert: {recommendation['stock_symbol']} - {recommendation['action']}"
    
    # Create email body
    body = f"""
Stock Investment Recommendation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Stock: {recommendation['stock_symbol']}
Action: {recommendation['action']}
Investment Amount: ${abs(recommendation['investment_amount'])}

Sentiment Analysis:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average Score: {recommendation['average_score']} (range: -1 to +1)
Confidence: {recommendation['confidence']:.1f}%

Vote Breakdown:
- Positive: {recommendation['positive_count']}
- Negative: {recommendation['negative_count']}
- Neutral: {recommendation['neutral_count']}
- Total Analyzed: {recommendation['total_analyzed']}

Reasoning: {recommendation['reasoning']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated recommendation from your AI Stock Advisor.
⚠️ Not financial advice. Always do your own research.
    """
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"✓ Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"✗ Email sending failed: {str(e)}")
        return False


# Optional: Test function
if __name__ == "__main__":
    # Test email sending
    test_recommendation = {
        'stock_symbol': 'AAPL',
        'action': 'BUY',
        'investment_amount': 500,
        'average_score': 0.65,
        'confidence': 75.0,
        'positive_count': 25,
        'negative_count': 10,
        'neutral_count': 5,
        'total_analyzed': 40,
        'reasoning': 'Strong positive sentiment detected'
    }
    
    test_email = "your_test_email@gmail.com"
    send_email_notification(test_recommendation, test_email)
