import sys
sys.path.append(".")
from tools.financial_news import get_financial_news

print("Fetching Apple news...")
print(get_financial_news.invoke("Apple"))

print("\n" + "="*60)
print("Fetching Tesla news...")
print(get_financial_news.invoke("Tesla"))

print("\n" + "="*60)
print("Fetching Indian stock market news...")
print(get_financial_news.invoke("Indian stock market"))