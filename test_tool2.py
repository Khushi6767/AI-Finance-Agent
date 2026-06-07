import sys
sys.path.append(".")
from tools.stock_history import get_stock_history

print("Apple - Last 1 month...")
print(get_stock_history.invoke("AAPL 1mo"))

print("\nTesla - Last 3 months...")
print(get_stock_history.invoke("TSLA 3mo"))

print("\nReliance - Last 1 week...")
print(get_stock_history.invoke("RELIANCE.NS 1wk"))