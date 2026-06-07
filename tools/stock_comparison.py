import yfinance as yf
from textblob import TextBlob
import requests
import os
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

def get_sentiment_score(company: str) -> float:
    """Helper to get quick sentiment score for comparison"""
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return 0.0
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f"{company} stock",
            "apiKey": api_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5
        }
        response = requests.get(url, params=params)
        data = response.json()
        articles = data.get("articles", [])
        if not articles:
            return 0.0
        total = 0
        for article in articles:
            text = f"{article.get('title','')}. {article.get('description','')}"
            blob = TextBlob(text)
            total += blob.sentiment.polarity
        return round(total / len(articles), 3)
    except:
        return 0.0

@tool
def compare_stocks(input_str: str) -> str:
    """
    Compares two stocks side by side on price, performance, fundamentals,
    technical indicators, and news sentiment. Gives a final recommendation
    on which stock is better to invest in.
    Input format: 'TICKER1 TICKER2' separated by space.
    Examples: 'AAPL MSFT', 'TSLA RIVN', 'RELIANCE.NS TCS.NS', 'INFY.NS WIPRO.NS'
    Use this when user asks to compare two stocks, wants to know which
    stock is better, or asks 'should I buy X or Y?'
    """
    try:
        parts = input_str.strip().split()
        if len(parts) != 2:
            return "Please provide exactly 2 tickers. Example: 'AAPL MSFT'"

        ticker1 = parts[0].upper()
        ticker2 = parts[1].upper()

        # Fetch data for both stocks
        stock1 = yf.Ticker(ticker1)
        stock2 = yf.Ticker(ticker2)

        info1 = stock1.info
        info2 = stock2.info

        # Basic info
        name1 = info1.get("longName", ticker1)
        name2 = info2.get("longName", ticker2)
        currency1 = info1.get("currency", "USD")
        currency2 = info2.get("currency", "USD")

        # Price data
        price1 = info1.get("currentPrice") or info1.get("regularMarketPrice", 0)
        price2 = info2.get("currentPrice") or info2.get("regularMarketPrice", 0)

        # Fundamental metrics
        pe1 = info1.get("trailingPE", 0)
        pe2 = info2.get("trailingPE", 0)

        pb1 = info1.get("priceToBook", 0)
        pb2 = info2.get("priceToBook", 0)

        roe1 = info1.get("returnOnEquity", 0)
        roe2 = info2.get("returnOnEquity", 0)

        profit_margin1 = info1.get("profitMargins", 0)
        profit_margin2 = info2.get("profitMargins", 0)

        debt_equity1 = info1.get("debtToEquity", 0)
        debt_equity2 = info2.get("debtToEquity", 0)

        revenue_growth1 = info1.get("revenueGrowth", 0)
        revenue_growth2 = info2.get("revenueGrowth", 0)

        market_cap1 = info1.get("marketCap", 0)
        market_cap2 = info2.get("marketCap", 0)

        dividend1 = info1.get("dividendYield", 0) or 0
        dividend2 = info2.get("dividendYield", 0) or 0

        # Historical performance
        hist1_1m = stock1.history(period="1mo")
        hist2_1m = stock2.history(period="1mo")
        hist1_3m = stock1.history(period="3mo")
        hist2_3m = stock2.history(period="3mo")

        def calc_return(hist):
            if hist.empty or len(hist) < 2:
                return 0
            return round(((hist["Close"].iloc[-1] - hist["Close"].iloc[0])
                         / hist["Close"].iloc[0]) * 100, 2)

        return1_1m = calc_return(hist1_1m)
        return2_1m = calc_return(hist2_1m)
        return1_3m = calc_return(hist1_3m)
        return2_3m = calc_return(hist2_3m)

        # RSI for both
        def calc_rsi(hist):
            if hist.empty or len(hist) < 15:
                return 50
            delta = hist["Close"].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return round(rsi.iloc[-1], 2)

        rsi1 = calc_rsi(hist1_3m)
        rsi2 = calc_rsi(hist2_3m)

        # Sentiment scores
        print(f"   Fetching sentiment for {name1}...")
        sentiment1 = get_sentiment_score(name1.split()[0])
        print(f"   Fetching sentiment for {name2}...")
        sentiment2 = get_sentiment_score(name2.split()[0])

        sentiment1_score = round((sentiment1 + 1) / 2 * 100, 1)
        sentiment2_score = round((sentiment2 + 1) / 2 * 100, 1)

        # Format market cap
        def fmt_mcap(mcap):
            if mcap >= 1_000_000_000_000:
                return f"{mcap/1_000_000_000_000:.2f}T"
            elif mcap >= 1_000_000_000:
                return f"{mcap/1_000_000_000:.2f}B"
            return f"{mcap/1_000_000:.2f}M"

        # ── SCORING SYSTEM ────────────────────────────────
        score1 = 0
        score2 = 0
        scoring_details = []

        # 1. 1 Month Return
        if return1_1m > return2_1m:
            score1 += 1
            scoring_details.append(f"✅ {ticker1} better 1M return")
        elif return2_1m > return1_1m:
            score2 += 1
            scoring_details.append(f"✅ {ticker2} better 1M return")

        # 2. 3 Month Return
        if return1_3m > return2_3m:
            score1 += 1
            scoring_details.append(f"✅ {ticker1} better 3M return")
        elif return2_3m > return1_3m:
            score2 += 1
            scoring_details.append(f"✅ {ticker2} better 3M return")

        # 3. P/E Ratio (lower is better — cheaper valuation)
        if pe1 and pe2:
            if 0 < pe1 < pe2:
                score1 += 1
                scoring_details.append(f"✅ {ticker1} lower P/E (cheaper)")
            elif 0 < pe2 < pe1:
                score2 += 1
                scoring_details.append(f"✅ {ticker2} lower P/E (cheaper)")

        # 4. ROE (higher is better)
        if roe1 and roe2:
            if roe1 > roe2:
                score1 += 1
                scoring_details.append(f"✅ {ticker1} higher ROE")
            elif roe2 > roe1:
                score2 += 1
                scoring_details.append(f"✅ {ticker2} higher ROE")

        # 5. Profit Margin (higher is better)
        if profit_margin1 and profit_margin2:
            if profit_margin1 > profit_margin2:
                score1 += 1
                scoring_details.append(f"✅ {ticker1} higher profit margin")
            elif profit_margin2 > profit_margin1:
                score2 += 1
                scoring_details.append(f"✅ {ticker2} higher profit margin")

        # 6. Revenue Growth (higher is better)
        if revenue_growth1 and revenue_growth2:
            if revenue_growth1 > revenue_growth2:
                score1 += 1
                scoring_details.append(f"✅ {ticker1} higher revenue growth")
            elif revenue_growth2 > revenue_growth1:
                score2 += 1
                scoring_details.append(f"✅ {ticker2} higher revenue growth")

        # 7. Sentiment Score
        if sentiment1 > sentiment2:
            score1 += 1
            scoring_details.append(f"✅ {ticker1} better news sentiment")
        elif sentiment2 > sentiment1:
            score2 += 1
            scoring_details.append(f"✅ {ticker2} better news sentiment")

        # Final verdict
        total = score1 + score2
        if score1 > score2:
            winner = ticker1
            winner_name = name1
            confidence = round(score1/total * 100) if total > 0 else 50
        elif score2 > score1:
            winner = ticker2
            winner_name = name2
            confidence = round(score2/total * 100) if total > 0 else 50
        else:
            winner = "TIE"
            winner_name = "Both equally matched"
            confidence = 50

        # Format percentages
        def fmt_pct(val):
            if val:
                return f"{round(val*100, 2)}%"
            return "N/A"

        return_emoji1 = "📈" if return1_1m > 0 else "📉"
        return_emoji2 = "📈" if return2_1m > 0 else "📉"

        output = f"""
╔══════════════════════════════════════════════════════╗
   ⚖️  STOCK COMPARISON: {ticker1} vs {ticker2}
╚══════════════════════════════════════════════════════╝

{'METRIC':<28} {ticker1:<18} {ticker2}
{'─'*65}
{'Company':<28} {name1[:16]:<18} {name2[:16]}
{'Current Price':<28} {f'{currency1} {price1}':<18} {f'{currency2} {price2}'}
{'Market Cap':<28} {fmt_mcap(market_cap1):<18} {fmt_mcap(market_cap2)}

━━━ PERFORMANCE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{'1 Month Return':<28} {f'{return_emoji1} {return1_1m}%':<18} {f'{return_emoji2} {return2_1m}%'}
{'3 Month Return':<28} {f'{"📈" if return1_3m>0 else "📉"} {return1_3m}%':<18} {f'{"📈" if return2_3m>0 else "📉"} {return2_3m}%'}
{'RSI (14)':<28} {rsi1:<18} {rsi2}

━━━ FUNDAMENTALS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{'P/E Ratio':<28} {str(round(pe1,2)) if pe1 else 'N/A':<18} {str(round(pe2,2)) if pe2 else 'N/A'}
{'Price/Book':<28} {str(round(pb1,2)) if pb1 else 'N/A':<18} {str(round(pb2,2)) if pb2 else 'N/A'}
{'Return on Equity':<28} {fmt_pct(roe1):<18} {fmt_pct(roe2)}
{'Profit Margin':<28} {fmt_pct(profit_margin1):<18} {fmt_pct(profit_margin2)}
{'Revenue Growth':<28} {fmt_pct(revenue_growth1):<18} {fmt_pct(revenue_growth2)}
{'Debt/Equity':<28} {str(round(debt_equity1,2)) if debt_equity1 else 'N/A':<18} {str(round(debt_equity2,2)) if debt_equity2 else 'N/A'}
{'Dividend Yield':<28} {fmt_pct(dividend1):<18} {fmt_pct(dividend2)}

━━━ SENTIMENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{'News Sentiment Score':<28} {f'{sentiment1_score}/100':<18} {f'{sentiment2_score}/100'}

━━━ SCORING SUMMARY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{ticker1} Score : {score1}/{total} criteria won
{ticker2} Score : {score2}/{total} criteria won

Scoring Details:
""" + "\n".join([f"  {d}" for d in scoring_details]) + f"""

━━━ FINAL VERDICT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 WINNER: {winner} ({winner_name})
   Confidence: {confidence}%

⚠️  Disclaimer: This comparison is for educational purposes.
    Past performance does not guarantee future results.
    Always do your own research before investing.
        """.strip()

        return output

    except Exception as e:
        return f"Error comparing stocks '{input_str}': {str(e)}"