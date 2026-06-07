import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

@tool
def web_search(query: str) -> str:
    """
    Use this tool to search the web for any general financial question,
    concept, or topic that cannot be answered by other tools.
    Use this for questions like 'What is inflation?', 'How does FD work?',
    'What is Sensex?', 'Explain mutual funds', 'What is P/E ratio?',
    'How does RBI affect stock market?', or any finance concept.
    Input should be a clear search query string.
    This is a fallback tool for general financial knowledge questions.
    """
    try:
        api_key = os.getenv("TAVILY_API_KEY")

        # If no Tavily key, use a backup approach with NewsAPI
        if not api_key:
            news_key = os.getenv("NEWS_API_KEY")
            if not news_key:
                return fallback_finance_answer(query)

            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": news_key,
                "language": "en",
                "sortBy": "relevancy",
                "pageSize": 3
            }
            response = requests.get(url, params=params)
            data = response.json()

            if data.get("status") != "ok" or not data.get("articles"):
                return fallback_finance_answer(query)

            articles = data["articles"]
            result = f"Search Results for: '{query}'\n"
            result += "=" * 50 + "\n"

            for i, article in enumerate(articles, 1):
                title = article.get("title", "No title")
                source = article.get("source", {}).get("name", "Unknown")
                description = article.get("description") or "No description."
                if len(description) > 200:
                    description = description[:200] + "..."
                result += f"\n{i}. {title}\n"
                result += f"   Source: {source}\n"
                result += f"   {description}\n"

            return result

        # If Tavily key exists, use Tavily
        else:
            url = "https://api.tavily.com/search"
            headers = {"Content-Type": "application/json"}
            payload = {
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": 3
            }
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()

            results = data.get("results", [])
            if not results:
                return fallback_finance_answer(query)

            output = f"Search Results for: '{query}'\n"
            output += "=" * 50 + "\n"

            for i, r in enumerate(results, 1):
                title = r.get("title", "No title")
                content = r.get("content", "No content")
                if len(content) > 200:
                    content = content[:200] + "..."
                output += f"\n{i}. {title}\n   {content}\n"

            return output

    except Exception as e:
        return fallback_finance_answer(query)


def fallback_finance_answer(query: str) -> str:
    """Basic answers for common finance questions when APIs fail"""

    query_lower = query.lower()

    knowledge = {
        "inflation": "Inflation is the rate at which prices of goods and services rise over time, reducing purchasing power of money. RBI targets 4% inflation in India.",
        "mutual fund": "A mutual fund pools money from many investors and invests in stocks, bonds, or other assets. Managed by professional fund managers. SIP (Systematic Investment Plan) lets you invest small amounts monthly.",
        "sensex": "Sensex is the benchmark index of Bombay Stock Exchange (BSE), tracking 30 largest Indian companies. It reflects overall Indian market health.",
        "nifty": "Nifty 50 is NSE's benchmark index tracking 50 largest Indian companies across sectors. It's the most widely tracked Indian market index.",
        "p/e ratio": "Price-to-Earnings ratio = Stock Price / Earnings per Share. Lower P/E may mean undervalued, higher P/E may mean overvalued. Indian market average P/E is around 20-25.",
        "fd": "Fixed Deposit is a safe investment where you deposit money with a bank for fixed period at fixed interest rate (6-7% in India). Capital is guaranteed.",
        "rbi": "Reserve Bank of India is India's central bank. It controls money supply, sets interest rates (repo rate), and regulates banks to control inflation and economic growth.",
        "dividend": "Dividend is a portion of company profits paid to shareholders. If you own 100 shares and company declares Rs 5 dividend, you get Rs 500.",
        "ipo": "Initial Public Offering is when a private company sells shares to public for first time on stock exchange. Investors can apply and get allotment.",
        "bull market": "Bull market means stock prices are rising consistently, economy is strong, investors are confident. Opposite is bear market where prices fall.",
    }

    for keyword, answer in knowledge.items():
        if keyword in query_lower:
            return f"Answer for '{query}':\n{answer}"

    return f"I searched for '{query}' but couldn't find specific results. Please try asking about a specific stock, company news, or portfolio analysis instead."