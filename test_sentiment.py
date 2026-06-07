import sys
sys.path.append(".")
from tools.sentiment_analysis import get_sentiment_analysis

print("Apple Sentiment Analysis...")
print(get_sentiment_analysis.invoke("Apple"))

print("\n" + "="*60)
print("Tesla Sentiment Analysis...")
print(get_sentiment_analysis.invoke("Tesla"))