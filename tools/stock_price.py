import yfinance as yf
from langchain_core.tools import tool

@tool
def get_stock_price(ticker: str) -> str:
    """
    Use this tool to get the current live stock price of any company.
    Input must be a valid stock ticker symbol like AAPL for Apple,
    TSLA for Tesla, MSFT for Microsoft, GOOGL for Google, RELIANCE.NS
    for Reliance Industries (Indian stocks end with .NS).
    Returns current price, day high, day low, and market cap.
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        day_high = info.get("dayHigh")
        day_low = info.get("dayLow")
        market_cap = info.get("marketCap")
        company_name = info.get("longName", ticker)
        currency = info.get("currency", "USD")

        if not current_price:
            return f"Could not fetch price for {ticker}. Please check if the ticker symbol is correct."

        # Format market cap nicely
        if market_cap:
            if market_cap >= 1_000_000_000_000:
                market_cap_str = f"{market_cap/1_000_000_000_000:.2f}T"
            elif market_cap >= 1_000_000_000:
                market_cap_str = f"{market_cap/1_000_000_000:.2f}B"
            else:
                market_cap_str = f"{market_cap/1_000_000:.2f}M"
        else:
            market_cap_str = "N/A"

        return f"""
Stock: {company_name} ({ticker.upper()})
Current Price: {currency} {current_price}
Day High: {currency} {day_high}
Day Low: {currency} {day_low}
Market Cap: {market_cap_str}
        """.strip()

    except Exception as e:
        return f"Error fetching stock data for {ticker}: {str(e)}"