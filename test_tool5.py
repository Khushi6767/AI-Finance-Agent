import sys
sys.path.append(".")
from tools.web_search import web_search

print("Test 1: What is inflation?")
print(web_search.invoke("What is inflation?"))

print("\n" + "="*60)
print("Test 2: How does mutual fund work?")
print(web_search.invoke("How does mutual fund work in India?"))

print("\n" + "="*60)
print("Test 3: What is Sensex?")
print(web_search.invoke("What is Sensex and how does it work?"))