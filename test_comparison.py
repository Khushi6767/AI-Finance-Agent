import sys
sys.path.append(".")
from tools.stock_comparison import compare_stocks

print("Comparing Apple vs Microsoft...")
print(compare_stocks.invoke("AAPL MSFT"))

print("\n" + "="*60)
print("Comparing Reliance vs TCS...")
print(compare_stocks.invoke("RELIANCE.NS TCS.NS"))