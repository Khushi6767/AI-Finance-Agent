import sys
sys.path.append(".")
from tools.technical_analysis import get_technical_analysis

print("Apple Technical Analysis...")
print(get_technical_analysis.invoke("AAPL 6mo"))

print("\n" + "="*60)
print("Reliance Technical Analysis...")
print(get_technical_analysis.invoke("RELIANCE.NS 3mo"))