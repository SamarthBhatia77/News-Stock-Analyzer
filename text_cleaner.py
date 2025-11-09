import re
import emoji

def clean_text(text):
    """
    Removes emojis, hashtags, mentions, URLs, and special characters
    Returns clean text ready for sentiment analysis
    """
    if not text:
        return ""
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove mentions (@username)
    text = re.sub(r'@\w+', '', text)
    
    # Remove hashtags (#hashtag)
    text = re.sub(r'#\w+', '', text)
    
    # Remove emojis
    text = emoji.replace_emoji(text, replace='')
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove very short texts (less than 10 characters)
    if len(text) < 10:
        return ""
    
    return text.strip()

def clean_multiple_texts(texts):
    """
    Cleans a list of texts and filters out empty ones
    """
    cleaned = [clean_text(text) for text in texts]
    # Filter out empty strings
    return [text for text in cleaned if text]


# Test the cleaner
if __name__ == "__main__":
    sample = "🚀 $AAPL to the moon! 🌙 Check this out: https://example.com #stocks @elonmusk"
    print("Original:", sample)
    print("Cleaned:", clean_text(sample))
    # Output: "AAPL to the moon Check this out"
