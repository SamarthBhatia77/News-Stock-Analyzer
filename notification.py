"""
Notification Module
Sends emails and SMS with investment recommendations
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class NotificationHandler:
    def __init__(self):
        """Initialize notification handler"""
        self.gmail_address = os.getenv('GMAIL_ADDRESS')
        self.gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        logger.info("✅ Notification Handler initialized")
    
    def send_email_recommendation(self, recommendation: dict, recipient_email: str) -> bool:
        """
        Send investment recommendation via email
        
        Args:
            recommendation: Dict with recommendation data
            recipient_email: Email address to send to
        
        Returns:
            True if sent successfully, False otherwise
        """
        logger.info(f"\n📧 Sending email to {recipient_email}...")
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"📊 Stock Analysis: {recommendation['stock_ticker']} - {recommendation['action']}"
            msg['From'] = self.gmail_address
            msg['To'] = recipient_email
            
            # Create email body
            timestamp = recommendation['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            
            text = f"""
Stock Analysis Report
=====================

Stock: {recommendation['stock_ticker']}
Timestamp: {timestamp}
Action: {recommendation['action']}
Confidence: {recommendation['confidence']:.2%}
Sentiment Score: {recommendation['sentiment_score']:.4f}

Investment Recommendation: {recommendation['investment_percent']}% of portfolio

Reasoning:
{recommendation['reasoning']}

Data Points Analyzed: {recommendation.get('data_points', 'N/A')}

---
This is an automated analysis. Please do your own research before investing.
            """
            
            html = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto;">
      <h1>📊 Stock Analysis Report</h1>
      
      <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px;">
        <h2>{recommendation['stock_ticker']}</h2>
        <p><strong>Action:</strong> <span style="font-size: 24px; color: {'green' if recommendation['action'] == 'BUY' else 'red' if recommendation['action'] == 'SELL' else 'orange'};">{recommendation['action']}</span></p>
        <p><strong>Confidence:</strong> {recommendation['confidence']:.2%}</p>
        <p><strong>Sentiment Score:</strong> {recommendation['sentiment_score']:.4f}</p>
        <p><strong>Investment:</strong> {recommendation['investment_percent']}% of portfolio</p>
      </div>
      
      <div style="margin-top: 20px;">
        <h3>Analysis</h3>
        <p>{recommendation['reasoning']}</p>
      </div>
      
      <div style="margin-top: 20px; padding: 10px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
        <p><strong>⚠️ Disclaimer:</strong> This is an automated analysis. Please do your own research before investing.</p>
      </div>
      
      <p style="margin-top: 30px; color: #999; font-size: 12px;">
        Generated on {timestamp}
      </p>
    </div>
  </body>
</html>
            """
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.gmail_address, self.gmail_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully to {recipient_email}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to send email: {str(e)}")
            return False
    
    def send_sms_recommendation(self, recommendation: dict, phone_number: str) -> bool:
        """
        Send investment recommendation via SMS (requires Twilio)
        
        Args:
            recommendation: Dict with recommendation data
            phone_number: Phone number to send to
        
        Returns:
            True if sent successfully, False otherwise
        """
        logger.info(f"\n📱 Sending SMS to {phone_number}...")
        
        try:
            # TODO: Implement Twilio SMS integration
            # You'll need to:
            # 1. pip install twilio
            # 2. Add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN to .env
            # 3. Uncomment code below
            
            """
            from twilio.rest import Client
            
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
            
            client = Client(account_sid, auth_token)
            
            message_text = (
                f"Stock Alert: {recommendation['stock_ticker']}\n"
                f"Action: {recommendation['action']}\n"
                f"Confidence: {recommendation['confidence']:.0%}\n"
                f"Sentiment: {recommendation['sentiment_score']:.2f}"
            )
            
            message = client.messages.create(
                body=message_text,
                from_=twilio_number,
                to=phone_number
            )
            
            logger.info(f"✅ SMS sent successfully")
            return True
            """
            
            logger.warning(f"⚠️  SMS integration not yet implemented")
            return False
        
        except Exception as e:
            logger.error(f"❌ Failed to send SMS: {str(e)}")
            return False


# Test the notification handler
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    handler = NotificationHandler()
    
    test_recommendation = {
        'stock_ticker': 'AAPL',
        'action': 'BUY',
        'confidence': 0.85,
        'sentiment_score': 0.72,
        'investment_percent': 15,
        'reasoning': 'Strong positive sentiment based on recent earnings',
        'timestamp': datetime.now(),
        'data_points': 142
    }
    
    # Uncomment to test email
    # handler.send_email_recommendation(test_recommendation, 'your_email@gmail.com')
