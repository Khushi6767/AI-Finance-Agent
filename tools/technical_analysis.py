import yfinance as yf
import pandas as pd
from langchain_core.tools import tool

@tool
def get_technical_analysis(input_str: str) -> str:
    """
    Use this tool to perform technical analysis on any stock.
    Calculates RSI, Moving Averages (MA20, MA50, MA200), MACD,
    Bollinger Bands, and gives a BUY/SELL/HOLD signal.
    Input format: 'TICKER PERIOD' where period is 3mo, 6mo, or 1y.
    Examples: 'AAPL 6mo', 'TSLA 1y', 'RELIANCE.NS 3mo'
    Use this when user asks for technical analysis, trading signals,
    whether a stock is overbought or oversold, or wants indicators.
    """
    try:
        parts = input_str.strip().split()
        if len(parts) != 2:
            return "Please provide input as 'TICKER PERIOD'. Example: 'AAPL 6mo'"

        ticker = parts[0].upper()
        period = parts[1].lower()

        # Fetch historical data
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty or len(df) < 20:
            return f"Not enough data for technical analysis of {ticker}."

        company_name = stock.info.get("longName", ticker)
        currency = stock.info.get("currency", "USD")
        current_price = df["Close"].iloc[-1]

        # ── RSI Calculation ──────────────────────────────
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = round(rsi.iloc[-1], 2)

        if current_rsi > 70:
            rsi_signal = "🔴 OVERBOUGHT — Consider selling or waiting"
        elif current_rsi < 30:
            rsi_signal = "🟢 OVERSOLD — Potential buying opportunity"
        else:
            rsi_signal = "🟡 NEUTRAL — Normal trading range"

        # ── Moving Averages ──────────────────────────────
        ma20 = round(df["Close"].rolling(window=20).mean().iloc[-1], 2)
        ma50 = round(df["Close"].rolling(window=min(50, len(df))).mean().iloc[-1], 2)

        if len(df) >= 200:
            ma200 = round(df["Close"].rolling(window=200).mean().iloc[-1], 2)
            ma200_str = f"{currency} {ma200}"
        else:
            ma200 = None
            ma200_str = "Not enough data (need 200 days)"

        # MA Signal
        price = round(current_price, 2)
        if price > ma50:
            ma_signal = "🟢 BULLISH — Price above MA50 (uptrend)"
        else:
            ma_signal = "🔴 BEARISH — Price below MA50 (downtrend)"

        # ── MACD Calculation ─────────────────────────────
        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_val = round(macd_line.iloc[-1], 4)
        signal_val = round(signal_line.iloc[-1], 4)

        if macd_val > signal_val:
            macd_signal = "🟢 BULLISH — MACD above signal line (momentum up)"
        else:
            macd_signal = "🔴 BEARISH — MACD below signal line (momentum down)"

        # ── Bollinger Bands ──────────────────────────────
        bb_mid = df["Close"].rolling(window=20).mean()
        bb_std = df["Close"].rolling(window=20).std()
        bb_upper = round((bb_mid + 2 * bb_std).iloc[-1], 2)
        bb_lower = round((bb_mid - 2 * bb_std).iloc[-1], 2)

        if price > bb_upper:
            bb_signal = "🔴 Price above upper band — potentially overbought"
        elif price < bb_lower:
            bb_signal = "🟢 Price below lower band — potentially oversold"
        else:
            bb_signal = "🟡 Price within normal Bollinger Band range"

        # ── Volume Analysis ──────────────────────────────
        avg_volume = round(df["Volume"].mean())
        current_volume = round(df["Volume"].iloc[-1])
        volume_ratio = round(current_volume / avg_volume, 2)

        if volume_ratio > 1.5:
            volume_signal = f"🔴 HIGH volume ({volume_ratio}x average) — strong movement"
        elif volume_ratio < 0.5:
            volume_signal = f"🟡 LOW volume ({volume_ratio}x average) — weak movement"
        else:
            volume_signal = f"🟢 NORMAL volume ({volume_ratio}x average)"

        # ── Overall Signal ───────────────────────────────
        bullish_count = 0
        bearish_count = 0

        if current_rsi < 50:
            bullish_count += 1
        else:
            bearish_count += 1

        if price > ma50:
            bullish_count += 1
        else:
            bearish_count += 1

        if macd_val > signal_val:
            bullish_count += 1
        else:
            bearish_count += 1

        if bullish_count >= 2:
            overall = "🟢 BUY / ACCUMULATE"
        elif bearish_count >= 2:
            overall = "🔴 SELL / AVOID"
        else:
            overall = "🟡 HOLD / WAIT"

        return f"""
╔══════════════════════════════════════════════════╗
   📊 TECHNICAL ANALYSIS: {company_name} ({ticker})
╚══════════════════════════════════════════════════╝

Current Price : {currency} {price}
Analysis Period: {period}

━━━ RSI (14) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RSI Value : {current_rsi}
Signal    : {rsi_signal}

━━━ MOVING AVERAGES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MA20  : {currency} {ma20}
MA50  : {currency} {ma50}
MA200 : {ma200_str}
Signal: {ma_signal}

━━━ MACD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MACD Line   : {macd_val}
Signal Line : {signal_val}
Signal      : {macd_signal}

━━━ BOLLINGER BANDS ━━━━━━━━━━━━━━━━━━━━━━━━━━━
Upper Band : {currency} {bb_upper}
Lower Band : {currency} {bb_lower}
Signal     : {bb_signal}

━━━ VOLUME ANALYSIS ━━━━━━━━━━━━━━━━━━━━━━━━━━━
Signal: {volume_signal}

━━━ OVERALL SIGNAL ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{overall}
(Based on {bullish_count}/3 bullish indicators)

⚠️  Disclaimer: Technical analysis is not guaranteed.
    Always combine with fundamental analysis.
        """.strip()

    except Exception as e:
        return f"Error performing technical analysis for '{input_str}': {str(e)}"