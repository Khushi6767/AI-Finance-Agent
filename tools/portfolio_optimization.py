import numpy as np
import yfinance as yf
from scipy.optimize import minimize
from langchain_core.tools import tool

@tool
def optimize_portfolio(input_str: str) -> str:
    """
    Optimizes a stock portfolio using Modern Portfolio Theory to find
    the mathematically best allocation of stocks that maximizes returns
    while minimizing risk. Calculates Sharpe Ratio, Expected Returns,
    and Portfolio Volatility.
    Input format: 'TICKER1,TICKER2,TICKER3' comma separated tickers.
    Examples: 'AAPL,MSFT,TSLA', 'RELIANCE.NS,TCS.NS,INFY.NS,WIPRO.NS'
    Use this when user wants to know optimal portfolio allocation,
    how to distribute investment across stocks, or asks about
    portfolio optimization, best allocation, or risk-return tradeoff.
    """
    try:
        # Parse tickers
        tickers = [t.strip().upper() for t in input_str.split(",")]
        if len(tickers) < 2:
            return "Please provide at least 2 tickers. Example: 'AAPL,MSFT,TSLA'"
        if len(tickers) > 6:
            return "Maximum 6 tickers supported for optimization."

        print(f"   Fetching data for {', '.join(tickers)}...")

        # Fetch 1 year of historical data
        price_data = {}
        valid_tickers = []
        company_names = {}

        for ticker in tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            if not hist.empty and len(hist) > 50:
                price_data[ticker] = hist["Close"]
                company_names[ticker] = stock.info.get("longName", ticker)[:20]
                valid_tickers.append(ticker)

        if len(valid_tickers) < 2:
            return "Could not fetch enough data for optimization. Check ticker symbols."

        # Build returns dataframe
        import pandas as pd
        prices_df = pd.DataFrame(price_data)
        returns_df = prices_df.pct_change().dropna()

        # ── Portfolio Statistics ──────────────────────────
        mean_returns = returns_df.mean() * 252  # annualized
        cov_matrix = returns_df.cov() * 252     # annualized covariance
        n = len(valid_tickers)
        risk_free_rate = 0.06  # 6% risk free rate (India approx)

        def portfolio_performance(weights):
            ret = np.dot(weights, mean_returns)
            vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (ret - risk_free_rate) / vol
            return ret, vol, sharpe

        # ── Optimization ──────────────────────────────────
        constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
        bounds = tuple((0.05, 0.6) for _ in range(n))  # 5% to 60% per stock
        initial_weights = np.array([1/n] * n)

        # Maximize Sharpe Ratio
        def neg_sharpe(weights):
            _, _, sharpe = portfolio_performance(weights)
            return -sharpe

        result_sharpe = minimize(
            neg_sharpe,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )

        # Minimize Volatility (for conservative investors)
        def portfolio_volatility(weights):
            _, vol, _ = portfolio_performance(weights)
            return vol

        result_minvol = minimize(
            portfolio_volatility,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )

        # Equal weight portfolio for comparison
        equal_weights = np.array([1/n] * n)

        # Get results
        opt_weights = result_sharpe.x
        minvol_weights = result_minvol.x

        opt_ret, opt_vol, opt_sharpe = portfolio_performance(opt_weights)
        minvol_ret, minvol_vol, minvol_sharpe = portfolio_performance(minvol_weights)
        eq_ret, eq_vol, eq_sharpe = portfolio_performance(equal_weights)

        # ── Individual Stock Stats ────────────────────────
        individual_stats = []
        for i, ticker in enumerate(valid_tickers):
            ann_return = mean_returns[ticker]
            ann_vol = returns_df[ticker].std() * np.sqrt(252)
            individual_stats.append({
                "ticker": ticker,
                "name": company_names[ticker],
                "annual_return": round(ann_return * 100, 2),
                "annual_vol": round(ann_vol * 100, 2),
                "opt_weight": round(opt_weights[i] * 100, 2),
                "minvol_weight": round(minvol_weights[i] * 100, 2),
                "equal_weight": round(equal_weights[i] * 100, 2)
            })

        # ── Build Output ──────────────────────────────────
        output = f"""
╔══════════════════════════════════════════════════════╗
   🎯 PORTFOLIO OPTIMIZATION REPORT
   Modern Portfolio Theory Analysis
╚══════════════════════════════════════════════════════╝

Stocks Analyzed: {', '.join(valid_tickers)}
Data Period: 1 Year | Risk-Free Rate: {risk_free_rate*100}%

━━━ INDIVIDUAL STOCK PERFORMANCE ━━━━━━━━━━━━━━━━━━━━
{'Ticker':<15} {'Company':<22} {'Annual Return':<16} {'Volatility'}
{'─'*65}"""

        for s in individual_stats:
            ret_emoji = "📈" if s["annual_return"] > 0 else "📉"
            output += f"\n{s['ticker']:<15} {s['name']:<22} {ret_emoji} {s['annual_return']}%{'':<8} {s['annual_vol']}%"

        output += f"""

━━━ PORTFOLIO STRATEGY COMPARISON ━━━━━━━━━━━━━━━━━━━
{'Metric':<25} {'Max Sharpe':<18} {'Min Risk':<18} {'Equal Weight'}
{'─'*75}
{'Expected Return':<25} {round(opt_ret*100,2)}%{'':<13} {round(minvol_ret*100,2)}%{'':<13} {round(eq_ret*100,2)}%
{'Annual Volatility':<25} {round(opt_vol*100,2)}%{'':<13} {round(minvol_vol*100,2)}%{'':<13} {round(eq_vol*100,2)}%
{'Sharpe Ratio':<25} {round(opt_sharpe,3):<18} {round(minvol_sharpe,3):<18} {round(eq_sharpe,3)}

━━━ RECOMMENDED ALLOCATION (MAX SHARPE) ━━━━━━━━━━━━━
Best for: Aggressive to Moderate investors
Goal: Maximize return per unit of risk
"""
        for s in individual_stats:
            bar = "█" * int(s["opt_weight"] / 5)
            output += f"\n   {s['ticker']:<15} {s['opt_weight']:>6.2f}%  {bar}"

        output += f"""

━━━ CONSERVATIVE ALLOCATION (MIN RISK) ━━━━━━━━━━━━━━
Best for: Conservative investors
Goal: Minimize portfolio volatility
"""
        for s in individual_stats:
            bar = "█" * int(s["minvol_weight"] / 5)
            output += f"\n   {s['ticker']:<15} {s['minvol_weight']:>6.2f}%  {bar}"

        output += f"""

━━━ WHAT THESE NUMBERS MEAN ━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Sharpe Ratio: Measures return per unit of risk taken
   > 1.0 = Good | > 2.0 = Very Good | > 3.0 = Excellent

📈 Expected Return: Projected annual return based on 1yr history
⚡ Volatility: How much portfolio value can swing up/down

━━━ RECOMMENDATION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

        if opt_sharpe > 1.5:
            rec = "Strong — This portfolio has excellent risk-adjusted returns"
        elif opt_sharpe > 1.0:
            rec = "Good — Decent risk-adjusted returns, consider diversifying more"
        elif opt_sharpe > 0.5:
            rec = "Fair — Consider adding more stable stocks to improve Sharpe ratio"
        else:
            rec = "Weak — High risk relative to returns. Reconsider stock selection"

        output += f"""
Portfolio Quality: {rec}
Best Strategy: {'Max Sharpe (Aggressive)' if opt_sharpe > 1 else 'Min Risk (Conservative)'}

⚠️  Disclaimer: Based on historical data. Past performance
    does not guarantee future results. Consult a SEBI
    registered advisor before making investment decisions.
        """.strip()

        return output

    except Exception as e:
        return f"Error optimizing portfolio '{input_str}': {str(e)}"