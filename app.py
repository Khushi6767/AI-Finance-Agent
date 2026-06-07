import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
import pandas as pd
import sys
sys.path.append(".")
from agent import chat

# ── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="FinBot - AI Financial Advisor",
    page_icon="📈",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid #00d4aa;
    }
    .main-header h1 {
        color: #00d4aa;
        font-size: 2.8em;
        margin: 0;
        font-weight: 800;
    }
    .main-header p {
        color: #a0a0b0;
        margin: 8px 0 0 0;
        font-size: 1.1em;
    }
    .metric-card {
        background: #1e1e2e;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #00d4aa;
        margin: 5px 0;
    }
    .tool-badge {
        background: #0f3460;
        color: #00d4aa;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 0.8em;
        margin: 2px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📈 FinBot</h1>
    <p>Elite AI Financial Advisor | 9 Tools | Real-Time Data | Professional Analysis</p>
    <p style="color:#00d4aa; font-size:0.9em;">
        Powered by Groq LLaMA 3.3 • LangChain • Modern Portfolio Theory
    </p>
</div>
""", unsafe_allow_html=True)

# ── Helper Functions for Charts ───────────────────────────
def plot_stock_chart(ticker: str, period: str = "3mo"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
            return None
        company = stock.info.get("longName", ticker)
        currency = stock.info.get("currency", "USD")

        fig = go.Figure()

        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist["Open"],
            high=hist["High"],
            low=hist["Low"],
            close=hist["Close"],
            name=ticker,
            increasing_line_color="#00d4aa",
            decreasing_line_color="#ff4444"
        ))

        # Moving average
        ma20 = hist["Close"].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=ma20,
            name="MA20",
            line=dict(color="#ffaa00", width=1.5)
        ))

        fig.update_layout(
            title=f"{company} ({ticker}) - {period} Price Chart",
            yaxis_title=f"Price ({currency})",
            xaxis_title="Date",
            template="plotly_dark",
            height=400,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117"
        )
        return fig
    except:
        return None

def plot_portfolio_pie(portfolio_str: str):
    try:
        import yfinance as yf
        entries = portfolio_str.strip().split(",")
        labels = []
        values = []
        for entry in entries:
            parts = entry.strip().split(":")
            if len(parts) == 3:
                ticker = parts[0].strip().upper()
                shares = float(parts[1].strip())
                stock = yf.Ticker(ticker)
                price = stock.info.get("currentPrice", 0)
                value = shares * price
                labels.append(ticker)
                values.append(value)

        if not labels:
            return None

        fig = px.pie(
            values=values,
            names=labels,
            title="Portfolio Allocation by Current Value",
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0e1117",
            height=350
        )
        return fig
    except:
        return None

def plot_comparison_bar(ticker1: str, ticker2: str):
    try:
        stock1 = yf.Ticker(ticker1)
        stock2 = yf.Ticker(ticker2)

        hist1 = stock1.history(period="3mo")
        hist2 = stock2.history(period="3mo")

        if hist1.empty or hist2.empty:
            return None

        # Normalize to 100 for comparison
        norm1 = (hist1["Close"] / hist1["Close"].iloc[0]) * 100
        norm2 = (hist2["Close"] / hist2["Close"].iloc[0]) * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist1.index, y=norm1,
            name=ticker1,
            line=dict(color="#00d4aa", width=2)
        ))
        fig.add_trace(go.Scatter(
            x=hist2.index, y=norm2,
            name=ticker2,
            line=dict(color="#ff6b6b", width=2)
        ))

        fig.update_layout(
            title=f"{ticker1} vs {ticker2} — Normalized Performance (Base=100)",
            yaxis_title="Normalized Price",
            xaxis_title="Date",
            template="plotly_dark",
            height=380,
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117"
        )
        return fig
    except:
        return None

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 FinBot")
    st.markdown("*Elite AI Financial Advisor*")
    st.markdown("---")

    st.markdown("### 🛠️ 9 Active Tools")
    tools_list = [
        "📊 Live Stock Prices",
        "📈 Historical Trends",
        "📰 Financial News",
        "💼 Portfolio Analysis",
        "🔍 Web Search",
        "⚡ Technical Analysis",
        "🧠 Sentiment Analysis",
        "⚖️ Stock Comparison",
        "🎯 Portfolio Optimization"
    ]
    for t in tools_list:
        st.markdown(f"<span class='tool-badge'>{t}</span>",
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 Quick Questions")
    quick_questions = [
        "Should I buy Apple stock?",
        "Technical analysis of TSLA",
        "Compare AAPL and MSFT",
        "Sentiment analysis of Tesla",
        "Optimize portfolio: AAPL,MSFT,TSLA",
        "Analyze portfolio: AAPL:10:150,TSLA:5:200",
        "How has Reliance.NS performed?",
        "Compare RELIANCE.NS and TCS.NS",
        "What is a Sharpe ratio?",
        "Latest news on Infosys"
    ]
    for q in quick_questions:
        if st.button(q, use_container_width=True, key=f"btn_{q}"):
            st.session_state.pending_question = q

    st.markdown("---")

    # Chart section in sidebar
    st.markdown("### 📊 Quick Chart")
    chart_ticker = st.text_input("Enter ticker:", value="AAPL",
                                  placeholder="AAPL, TSLA, RELIANCE.NS")
    chart_period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y"])
    if st.button("📈 Show Chart", use_container_width=True):
        st.session_state.chart_ticker = chart_ticker
        st.session_state.chart_period = chart_period

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <small>
    ⚠️ <b>Disclaimer:</b> Educational purposes only.
    Not SEBI registered advice. Consult a certified
    financial advisor before investing.
    </small>
    """, unsafe_allow_html=True)

# ── Main Area ─────────────────────────────────────────────
# Show quick chart if requested
if "chart_ticker" in st.session_state and st.session_state.chart_ticker:
    ticker = st.session_state.chart_ticker
    period = st.session_state.get("chart_period", "3mo")
    with st.spinner(f"Loading chart for {ticker}..."):
        fig = plot_stock_chart(ticker, period)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    st.session_state.chart_ticker = None

# ── Chat Interface ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# Welcome message
if not st.session_state.messages:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
        <b>📊 Stock Analysis</b><br>
        <small>"Should I buy Apple stock right now?"</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
        <b>⚖️ Stock Comparison</b><br>
        <small>"Compare Reliance vs TCS for long term"</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
        <b>🎯 Optimization</b><br>
        <small>"Optimize my portfolio: AAPL,MSFT,TSLA"</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 👋 Welcome to FinBot!")
    st.markdown("""
    I use **9 specialized tools** and real-time market data to give you
    professional financial analysis. Ask me anything about stocks,
    portfolios, market trends, or investment strategies!
    """)

# Display chat history
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        # Show charts if stored
        if "chart" in message and message["chart"] is not None:
            st.plotly_chart(message["chart"], use_container_width=True)
        if "pie_chart" in message and message["pie_chart"] is not None:
            st.plotly_chart(message["pie_chart"], use_container_width=True)
        if "comparison_chart" in message and message["comparison_chart"] is not None:
            st.plotly_chart(message["comparison_chart"], use_container_width=True)

def process_message(user_input: str):
    """Process user message and generate response with charts"""
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔍 FinBot is analyzing with multiple tools..."):
            response = chat(user_input)

        st.markdown(response)

        # Auto generate relevant charts
        chart = None
        pie_chart = None
        comparison_chart = None

        user_lower = user_input.lower()

        # Stock chart for single stock questions
        tickers_to_check = [
            "AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "META",
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "WIPRO.NS",
            "HDFCBANK.NS", "ICICIBANK.NS"
        ]

        # Comparison chart
        words = user_input.upper().split()
        if "COMPARE" in user_lower or "VS" in user_lower:
            found = [t for t in tickers_to_check if t in words or
                     t.replace(".NS", "") in words]
            if len(found) >= 2:
                with st.spinner("📊 Generating comparison chart..."):
                    comparison_chart = plot_comparison_bar(found[0], found[1])
                if comparison_chart:
                    st.plotly_chart(comparison_chart, use_container_width=True)

        # Portfolio pie chart
        elif "ANALYZE PORTFOLIO" in user_input.upper() or \
             ("portfolio" in user_lower and ":" in user_input):
            portfolio_part = user_input
            for word in ["analyze portfolio:", "portfolio:", "analyze my portfolio:"]:
                portfolio_part = portfolio_part.lower().replace(word, "").strip()
            with st.spinner("🥧 Generating portfolio chart..."):
                pie_chart = plot_portfolio_pie(portfolio_part.upper())
            if pie_chart:
                st.plotly_chart(pie_chart, use_container_width=True)

        # Single stock chart
        else:
            for t in tickers_to_check:
                if t in user_input.upper() or t.replace(".NS", "") in user_input.upper():
                    with st.spinner(f"📈 Generating {t} chart..."):
                        chart = plot_stock_chart(t, "3mo")
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                    break

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "chart": chart,
            "pie_chart": pie_chart,
            "comparison_chart": comparison_chart
        })

# Handle sidebar button clicks
if st.session_state.pending_question:
    user_input = st.session_state.pending_question
    st.session_state.pending_question = None
    process_message(user_input)
    st.rerun()

# Handle typed input
user_input = st.chat_input("Ask FinBot anything — stocks, portfolio, markets...")
if user_input:
    process_message(user_input)
    st.rerun()