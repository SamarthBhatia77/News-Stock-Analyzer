"""
Text Cleaning and Preprocessing Module
Cleans scraped data for ML model input
"""

import re
import emoji
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    def __init__(self):
        """Initialize text cleaner"""
        logger.info("✅ Text Cleaner initialized")
    
    @staticmethod
    def remove_urls(text: str) -> str:
        """Remove URLs from text"""
        return re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    @staticmethod
    def remove_mentions(text: str) -> str:
        """Remove @mentions from text"""
        return re.sub(r'@\w+', '', text)
    
    @staticmethod
    def remove_hashtags(text: str) -> str:
        """Remove #hashtags from text"""
        return re.sub(r'#\w+', '', text)
    
    @staticmethod
    def remove_emojis(text: str) -> str:
        """Remove emojis from text"""
        return emoji.replace_emoji(text, replace="")
    
    @staticmethod
    def remove_special_chars(text: str) -> str:
        """Remove special characters"""
        return re.sub(r'[^a-zA-Z0-9\s\.\!\?]', '', text)
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Remove extra whitespace"""
        return ' '.join(text.split())
    
    @staticmethod
    def lowercase(text: str) -> str:
        """Convert to lowercase"""
        return text.lower()
    
    def clean_single_text(self, text: str) -> str:
        """
        Clean a single text string through all preprocessing steps
        
        Args:
            text: Raw text to clean
        
        Returns:
            Cleaned text ready for ML model
        """
        # Apply cleaning steps in order
        text = self.remove_urls(text)
        text = self.remove_mentions(text)
        text = self.remove_hashtags(text)
        text = self.remove_emojis(text)
        text = self.remove_special_chars(text)
        text = self.normalize_whitespace(text)
        text = self.lowercase(text)
        
        return text
    
    def clean_multiple_texts(self, texts: list) -> list:
        """
        Clean multiple text strings
        
        Args:
            texts: List of raw text strings
        
        Returns:
            List of cleaned text strings
        """
        cleaned = []
        for text in texts:
            if text:  # Only clean non-empty texts
                cleaned_text = self.clean_single_text(text)
                if cleaned_text:  # Only add non-empty results
                    cleaned.append(cleaned_text)
        
        logger.info(f"✅ Cleaned {len(cleaned)}/{len(texts)} texts")
        return cleaned
    
    def clean_scraper_output(self, raw_data: list) -> list:
        """
        Clean raw scraper output
        
        Args:
            raw_data: List of dicts from scrapers with 'text' key
        
        Returns:
            List of cleaned data dicts with 'cleaned_text' key added
        """
        for item in raw_data:
            if 'text' in item:
                item['cleaned_text'] = self.clean_single_text(item['text'])
        
        return raw_data


# Test the cleaner
if __name__ == "__main__":
    cleaner = TextCleaner()
    
    test_texts = [
        "🚀 $AAPL to the moon! 🌙 Check this out: https://example.com @elonmusk #stocks",
        "Apple $AAPL earnings beat expectations!!! #AAPL",
        "This is a normal tweet without special chars"
    ]
    
    cleaned = cleaner.clean_multiple_texts(test_texts)
    for original, cleaned_text in zip(test_texts, cleaned):
        print(f"Original: {original}")
        print(f"Cleaned:  {cleaned_text}\n")
