import yfinance as yf
from langchain_core.tools import tool

@tool
def get_stock_history(input_str: str) -> str:
    """
    Gets historical price performance of a stock.
    Input format is TICKER PERIOD like: AAPL 1mo or HDFCBANK.NS 3mo
    Valid periods: 1wk, 1mo, 3mo, 6mo, 1y
    """
    try:
        # Split input into ticker and period
        parts = input_str.strip().split()
        if len(parts) != 2:
            return "Please provide input as 'TICKER PERIOD'. Example: 'AAPL 1mo'"
        
        ticker = parts[0].upper()
        period = parts[1].lower()

        valid_periods = ["1wk", "1mo", "3mo", "6mo", "1y"]
        if period not in valid_periods:
            return f"Invalid period. Choose from: {', '.join(valid_periods)}"

        stock = yf.Ticker(ticker)
        history = stock.history(period=period)

        if history.empty:
            return f"No historical data found for {ticker}."

        # Get key price points
        start_price = round(history["Close"].iloc[0], 2)
        end_price = round(history["Close"].iloc[-1], 2)
        highest = round(history["Close"].max(), 2)
        lowest = round(history["Close"].min(), 2)
        avg_price = round(history["Close"].mean(), 2)

        # Calculate percentage change
        change = round(((end_price - start_price) / start_price) * 100, 2)
        trend = "📈 UP" if change > 0 else "📉 DOWN"

        # Get last 5 closing prices for recent trend
        last_5 = history["Close"].tail(5).round(2).tolist()
        last_5_str = " → ".join([str(p) for p in last_5])

        company_name = stock.info.get("longName", ticker)
        currency = stock.info.get("currency", "USD")

        return f"""
Stock History: {company_name} ({ticker}) — Last {period}
Trend: {trend} ({change}%)
Start Price: {currency} {start_price}
Current Price: {currency} {end_price}
Highest in Period: {currency} {highest}
Lowest in Period: {currency} {lowest}
Average Price: {currency} {avg_price}
Last 5 Closing Prices: {last_5_str}
        """.strip()

    except Exception as e:
        return f"Error fetching history for input '{input_str}': {str(e)}"