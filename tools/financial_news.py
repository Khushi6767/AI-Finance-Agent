import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

@tool
def get_financial_news(company: str) -> str:
    """
    Fetches latest financial news about a company.
    Input is a simple company name like Apple, Tesla, HDFC Bank, Reliance.
    """
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return "NEWS_API_KEY not found in environment variables."

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f"{company} finance",
            "apiKey": api_key,
            "language": "en",
            "sortBy": "publishedAt",  # most recent first
            "pageSize": 5             # get 5 articles
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data.get("status") != "ok":
            return f"News API error: {data.get('message', 'Unknown error')}"

        articles = data.get("articles", [])
        if not articles:
            return f"No recent news found for '{company}'."

        # Format the news nicely
        result = f"Latest News for '{company}':\n"
        result += "=" * 50 + "\n"

        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            source = article.get("source", {}).get("name", "Unknown")
            published = article.get("publishedAt", "")[:10]  # just the date
            description = article.get("description") or "No description available."
            url_link = article.get("url", "")

            # Truncate long descriptions
            if len(description) > 150:
                description = description[:150] + "..."

            result += f"""
📰 Article {i}:
Title: {title}
Source: {source} | Date: {published}
Summary: {description}
Link: {url_link}
""" 
        return result.strip()

    except Exception as e:
        return f"Error fetching news for '{company}': {str(e)}"