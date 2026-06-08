from langchain_core.tools import tool

@tool
def get_risk_profile(answers: str) -> str:
    """
    Analyzes a user's risk profile based on their answers to financial
    profiling questions. Determines if they are Conservative, Moderate,
    or Aggressive investor and gives personalized investment guidelines.
    Input format: 'horizon:X,loss:X,income:X,experience:X,goal:X'
    where:
    - horizon: investment time (1=less than 1yr, 2=1-3yrs, 3=3-5yrs, 4=5+yrs)
    - loss: loss tolerance (1=cannot tolerate, 2=up to 10%, 3=up to 25%, 4=over 25%)
    - income: monthly income (1=under 25k, 2=25k-50k, 3=50k-1L, 4=over 1L)
    - experience: market experience (1=beginner, 2=some, 3=experienced, 4=expert)
    - goal: investment goal (1=capital preservation, 2=regular income, 3=growth, 4=aggressive growth)
    Use this tool when user wants to know their risk profile or asks
    for personalized investment advice setup.
    """
    try:
        # Parse answers
        profile_data = {}
        for item in answers.split(","):
            key, value = item.strip().split(":")
            profile_data[key.strip()] = int(value.strip())

        horizon = profile_data.get("horizon", 2)
        loss = profile_data.get("loss", 2)
        income = profile_data.get("income", 2)
        experience = profile_data.get("experience", 2)
        goal = profile_data.get("goal", 2)

        # Calculate risk score
        total_score = horizon + loss + income + experience + goal
        max_score = 20
        risk_percentage = (total_score / max_score) * 100

        # Determine profile
        if risk_percentage <= 35:
            profile = "CONSERVATIVE"
            profile_emoji = "🛡️"
            description = "You prioritize capital safety over returns"
            recommended_allocation = {
                "Large Cap Stocks": "20%",
                "Government Bonds/FD": "40%",
                "Debt Mutual Funds": "25%",
                "Gold/Commodities": "10%",
                "Cash/Liquid Funds": "5%"
            }
            stock_advice = [
                "Focus on blue-chip, dividend paying stocks only",
                "Avoid small-cap and mid-cap stocks",
                "Prefer PSU stocks (NTPC, COALINDIA, ONGC)",
                "Maximum 20% of portfolio in equities",
                "Prefer index funds over individual stocks",
                "Avoid leveraged trading or F&O completely"
            ]
            us_stocks = ["JNJ", "PG", "KO", "VZ", "T"]
            indian_stocks = ["HDFCBANK.NS", "ITC.NS", "COALINDIA.NS",
                           "NTPC.NS", "POWERGRID.NS"]
            risk_level = "LOW"
            expected_return = "8-12% annually"
            max_drawdown = "Should not exceed 10%"

        elif risk_percentage <= 65:
            profile = "MODERATE"
            profile_emoji = "⚖️"
            description = "You balance growth with reasonable risk"
            recommended_allocation = {
                "Large Cap Stocks": "35%",
                "Mid Cap Stocks": "15%",
                "Debt Mutual Funds": "20%",
                "Index Funds": "20%",
                "Gold/Commodities": "10%"
            }
            stock_advice = [
                "Mix of large-cap and select mid-cap stocks",
                "Diversify across 3-4 sectors minimum",
                "Can invest in index funds (Nifty 50, S&P 500)",
                "Rebalance portfolio every 6 months",
                "Keep 20% in debt for stability",
                "Avoid penny stocks and highly speculative trades"
            ]
            us_stocks = ["AAPL", "MSFT", "GOOGL", "BRK-B", "JPM"]
            indian_stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS",
                           "INFY.NS", "HINDUNILVR.NS"]
            risk_level = "MEDIUM"
            expected_return = "12-18% annually"
            max_drawdown = "Can tolerate up to 25% drawdown"

        else:
            profile = "AGGRESSIVE"
            profile_emoji = "🚀"
            description = "You prioritize maximum growth over safety"
            recommended_allocation = {
                "Large Cap Stocks": "30%",
                "Mid Cap Stocks": "25%",
                "Small Cap Stocks": "20%",
                "International Stocks": "15%",
                "Crypto/Alternatives": "10%"
            }
            stock_advice = [
                "Can invest across all market caps",
                "Sector rotation strategy recommended",
                "Can consider F&O for hedging (not speculation)",
                "Look for high growth, high PE stocks",
                "International diversification recommended",
                "Can hold concentrated positions (5-7 stocks)"
            ]
            us_stocks = ["NVDA", "TSLA", "META", "AMZN", "AMD"]
            indian_stocks = ["TATAMOTORS.NS", "ADANIENT.NS",
                           "ZOMATO.NS", "PAYTM.NS", "NYKAA.NS"]
            risk_level = "HIGH"
            expected_return = "18-30% annually"
            max_drawdown = "Can tolerate 40%+ drawdown"

        # Format allocation
        allocation_str = "\n".join([f"   {k:<28} {v}"
                                    for k, v in recommended_allocation.items()])

        # Format advice
        advice_str = "\n".join([f"   {i+1}. {a}"
                                for i, a in enumerate(stock_advice)])

        # Format stocks
        us_str = ", ".join(us_stocks)
        indian_str = ", ".join(indian_stocks)

        return f"""
╔══════════════════════════════════════════════════════╗
   {profile_emoji} INVESTOR RISK PROFILE ASSESSMENT
╚══════════════════════════════════════════════════════╝

Profile Type    : {profile} INVESTOR
Risk Level      : {risk_level}
Risk Score      : {total_score}/{max_score} ({round(risk_percentage)}%)
Description     : {description}

━━━ RECOMMENDED PORTFOLIO ALLOCATION ━━━━━━━━━━━━━━━━
{allocation_str}

━━━ PERSONALIZED INVESTMENT GUIDELINES ━━━━━━━━━━━━━━
{advice_str}

━━━ SUGGESTED STOCKS FOR YOUR PROFILE ━━━━━━━━━━━━━━━
🇺🇸 US Stocks    : {us_str}
🇮🇳 Indian Stocks: {indian_str}

━━━ RETURN EXPECTATIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Expected Annual Return : {expected_return}
Max Drawdown Tolerance : {max_drawdown}

━━━ WHAT THIS MEANS FOR YOU ━━━━━━━━━━━━━━━━━━━━━━━━━
All investment advice from FinBot will now be tailored
to your {profile} risk profile. When asking for stock
recommendations, FinBot will consider your risk tolerance,
investment horizon, and financial goals.

⚠️  Note: Risk profile should be reassessed every year
    or after major life changes.
        """.strip()

    except Exception as e:
        return f"Error analyzing risk profile: {str(e)}"