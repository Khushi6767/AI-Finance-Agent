import os
import requests
from textblob import TextBlob
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

def analyze_sentiment(text: str) -> dict:
    """Analyzes sentiment of a text using TextBlob"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 to +1
    subjectivity = blob.sentiment.subjectivity  # 0 to 1

    if polarity > 0.3:
        label = "VERY POSITIVE 🟢"
        emoji = "📈"
    elif polarity > 0.05:
        label = "POSITIVE 🟢"
        emoji = "📈"
    elif polarity < -0.3:
        label = "VERY NEGATIVE 🔴"
        emoji = "📉"
    elif polarity < -0.05:
        label = "NEGATIVE 🔴"
        emoji = "📉"
    else:
        label = "NEUTRAL 🟡"
        emoji = "➡️"

    return {
        "polarity": round(polarity, 3),
        "subjectivity": round(subjectivity, 3),
        "label": label,
        "emoji": emoji
    }

@tool
def get_sentiment_analysis(company: str) -> str:
    """
    Fetches latest news about a company and performs AI sentiment analysis
    on each article. Returns sentiment scores, overall market mood,
    and investment implications based on news sentiment.
    Use this when user wants to know market sentiment, public opinion,
    news mood, or whether news is positive or negative for a stock.
    Input is a company name like 'Apple', 'Tesla', 'Reliance', 'TCS'.
    """
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return "NEWS_API_KEY not found."

        # Fetch news
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f"{company} stock finance earnings",
            "apiKey": api_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 8
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data.get("status") != "ok":
            return f"News API error: {data.get('message')}"

        articles = data.get("articles", [])
        if not articles:
            return f"No news found for '{company}'."

        # Analyze sentiment of each article
        sentiments = []
        total_polarity = 0
        article_results = []

        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "") or ""
            source = article.get("source", {}).get("name", "Unknown")
            date = article.get("publishedAt", "")[:10]
            url_link = article.get("url", "")

            # Combine title and description for better analysis
            text_to_analyze = f"{title}. {description}"
            sentiment = analyze_sentiment(text_to_analyze)

            total_polarity += sentiment["polarity"]
            sentiments.append(sentiment["polarity"])

            article_results.append({
                "title": title[:80] + "..." if len(title) > 80 else title,
                "source": source,
                "date": date,
                "sentiment": sentiment,
                "url": url_link
            })

        # Overall sentiment
        avg_polarity = total_polarity / len(sentiments)
        positive_count = sum(1 for s in sentiments if s > 0.05)
        negative_count = sum(1 for s in sentiments if s < -0.05)
        neutral_count = len(sentiments) - positive_count - negative_count

        if avg_polarity > 0.2:
            overall_mood = "🟢 STRONGLY BULLISH"
            investment_implication = "News sentiment strongly favors buying. Market confidence is high."
        elif avg_polarity > 0.05:
            overall_mood = "🟢 BULLISH"
            investment_implication = "Mostly positive news. Cautiously optimistic outlook."
        elif avg_polarity < -0.2:
            overall_mood = "🔴 STRONGLY BEARISH"
            investment_implication = "Very negative news sentiment. Consider avoiding or selling."
        elif avg_polarity < -0.05:
            overall_mood = "🔴 BEARISH"
            investment_implication = "Negative news sentiment. Proceed with caution."
        else:
            overall_mood = "🟡 NEUTRAL"
            investment_implication = "Mixed or neutral news. Monitor closely before deciding."

        # Sentiment score as percentage (0-100)
        sentiment_score = round((avg_polarity + 1) / 2 * 100, 1)

        # Build output
        output = f"""
╔══════════════════════════════════════════════════╗
   🧠 SENTIMENT ANALYSIS: {company.upper()}
╚══════════════════════════════════════════════════╝

━━━ OVERALL MARKET SENTIMENT ━━━━━━━━━━━━━━━━━━━━
Sentiment Score  : {sentiment_score}/100
Overall Mood     : {overall_mood}
Avg Polarity     : {round(avg_polarity, 3)} (scale: -1 to +1)

Articles Analyzed: {len(articles)}
✅ Positive News : {positive_count} articles
❌ Negative News : {negative_count} articles  
➡️  Neutral News  : {neutral_count} articles

💡 Investment Implication:
{investment_implication}

━━━ INDIVIDUAL ARTICLE SENTIMENT ━━━━━━━━━━━━━━━
"""
        for i, article in enumerate(article_results, 1):
            s = article["sentiment"]
            output += f"""
{s['emoji']} Article {i}: [{s['label']}]
   Title  : {article['title']}
   Source : {article['source']} | {article['date']}
   Score  : {s['polarity']} polarity | {s['subjectivity']} subjectivity
"""

        output += f"""
━━━ SENTIMENT SUMMARY ━━━━━━━━━━━━━━━━━━━━━━━━━
Based on {len(articles)} recent news articles about {company}:
Overall market sentiment is {overall_mood}
Sentiment Score: {sentiment_score}/100

⚠️  Note: Sentiment analysis is based on news text only.
    Always combine with technical and fundamental analysis.
        """.strip()

        return output

    except Exception as e:
        return f"Error performing sentiment analysis for '{company}': {str(e)}"