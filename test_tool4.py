import sys
sys.path.append(".")
from tools.portfolio_analyzer import analyze_portfolio

print("Testing portfolio analysis...")
print("Portfolio: 10 Apple shares bought at $150, 5 Tesla at $200, 20 Reliance at 1200")
print()

result = analyze_portfolio.invoke("AAPL:10:150.00, TSLA:5:200.00, RELIANCE.NS:20:1200.00")
print(result)