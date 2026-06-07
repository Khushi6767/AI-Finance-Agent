import sys
sys.path.append(".")
from tools.portfolio_optimization import optimize_portfolio

print("Optimizing US Portfolio...")
print(optimize_portfolio.invoke("AAPL,MSFT,TSLA"))

print("\n" + "="*60)
print("Optimizing Indian Portfolio...")
print(optimize_portfolio.invoke("RELIANCE.NS,TCS.NS,INFY.NS,WIPRO.NS"))