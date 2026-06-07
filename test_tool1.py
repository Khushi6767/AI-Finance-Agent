import sys
sys.path.append(".")
from tools.stock_price import get_stock_price

# Test with Apple
print("Testing Apple (AAPL)...")
result = get_stock_price.invoke("AAPL")
print(result)

print("\nTesting Tesla (TSLA)...")
result = get_stock_price.invoke("TSLA")
print(result)

print("\nTesting Reliance (Indian stock)...")
result = get_stock_price.invoke("RELIANCE.NS")
print(result)