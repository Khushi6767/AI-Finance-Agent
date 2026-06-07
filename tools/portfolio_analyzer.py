import yfinance as yf
from langchain_core.tools import tool

@tool
def analyze_portfolio(portfolio_str: str) -> str:
    """
    Use this tool to analyze a user's stock portfolio. Calculate total
    portfolio value, individual stock values, profit or loss, and
    portfolio allocation percentage for each stock.
    Input format: 'TICKER1:SHARES1:BUYPRICE1, TICKER2:SHARES2:BUYPRICE2'
    Example: 'AAPL:10:150.00, TSLA:5:200.00, RELIANCE.NS:20:1200.00'
    Use this when user says they own stocks and wants to know their
    portfolio value, profit/loss, or how their investments are doing.
    """
    try:
        # Parse the portfolio string
        holdings = []
        entries = portfolio_str.strip().split(",")

        for entry in entries:
            parts = entry.strip().split(":")
            if len(parts) != 3:
                return f"Invalid format for entry '{entry}'. Use TICKER:SHARES:BUYPRICE format."

            ticker = parts[0].strip().upper()
            shares = float(parts[1].strip())
            buy_price = float(parts[2].strip())
            holdings.append((ticker, shares, buy_price))

        if not holdings:
            return "No valid holdings found. Please check your input format."

        # Fetch current prices and calculate values
        results = []
        total_invested = 0
        total_current_value = 0

        for ticker, shares, buy_price in holdings:
            stock = yf.Ticker(ticker)
            info = stock.info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            company_name = info.get("longName", ticker)
            currency = info.get("currency", "USD")

            if not current_price:
                results.append({
                    "ticker": ticker,
                    "company": company_name,
                    "error": "Could not fetch current price"
                })
                continue

            invested = shares * buy_price
            current_value = shares * current_price
            profit_loss = current_value - invested
            profit_loss_pct = ((current_price - buy_price) / buy_price) * 100

            total_invested += invested
            total_current_value += current_value

            results.append({
                "ticker": ticker,
                "company": company_name,
                "currency": currency,
                "shares": shares,
                "buy_price": buy_price,
                "current_price": current_price,
                "invested": round(invested, 2),
                "current_value": round(current_value, 2),
                "profit_loss": round(profit_loss, 2),
                "profit_loss_pct": round(profit_loss_pct, 2)
            })

        # Build the output
        total_profit_loss = total_current_value - total_invested
        total_profit_loss_pct = ((total_current_value - total_invested) / total_invested) * 100
        overall_trend = "📈 PROFIT" if total_profit_loss >= 0 else "📉 LOSS"

        output = "=" * 55 + "\n"
        output += "         📊 PORTFOLIO ANALYSIS REPORT\n"
        output += "=" * 55 + "\n\n"

        for r in results:
            if "error" in r:
                output += f"❌ {r['ticker']}: {r['error']}\n\n"
                continue

            emoji = "📈" if r["profit_loss"] >= 0 else "📉"
            allocation = (r["current_value"] / total_current_value) * 100

            output += f"{emoji} {r['company']} ({r['ticker']})\n"
            output += f"   Shares Owned    : {r['shares']}\n"
            output += f"   Buy Price       : {r['currency']} {r['buy_price']}\n"
            output += f"   Current Price   : {r['currency']} {r['current_price']}\n"
            output += f"   Amount Invested : {r['currency']} {r['invested']}\n"
            output += f"   Current Value   : {r['currency']} {r['current_value']}\n"
            output += f"   Profit / Loss   : {r['currency']} {r['profit_loss']} ({r['profit_loss_pct']}%)\n"
            output += f"   Portfolio Share : {round(allocation, 2)}%\n\n"

        output += "=" * 55 + "\n"
        output += f"   TOTAL INVESTED    : {round(total_invested, 2)}\n"
        output += f"   TOTAL VALUE NOW   : {round(total_current_value, 2)}\n"
        output += f"   OVERALL P&L       : {round(total_profit_loss, 2)} ({round(total_profit_loss_pct, 2)}%)\n"
        output += f"   STATUS            : {overall_trend}\n"
        output += "=" * 55

        return output

    except Exception as e:
        return f"Error analyzing portfolio: {str(e)}"