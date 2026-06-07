import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

# Import all tools
from tools.stock_price import get_stock_price
from tools.stock_history import get_stock_history
from tools.financial_news import get_financial_news
from tools.portfolio_analyzer import analyze_portfolio
from tools.web_search import web_search
from tools.technical_analysis import get_technical_analysis
from tools.sentiment_analysis import get_sentiment_analysis
from tools.stock_comparison import compare_stocks
from tools.portfolio_optimization import optimize_portfolio

load_dotenv()

# ── 1. Brain ─────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# ── 2. All 9 Tools ───────────────────────────────────────
tools = [
    get_stock_price,
    get_stock_history,
    get_financial_news,
    analyze_portfolio,
    web_search,
    get_technical_analysis,
    get_sentiment_analysis,
    compare_stocks,
    optimize_portfolio
]

# ── 3. System Prompt ─────────────────────────────────────
SYSTEM_PROMPT = """You are FinBot, an elite AI financial advisor with expertise 
in global and Indian stock markets. You provide data-driven, professional 
financial analysis using real-time market data.

You have access to these 9 specialized tools:
1. get_stock_price: Live stock prices and market cap
2. get_stock_history: Historical price trends and returns
3. get_financial_news: Latest news articles about companies
4. analyze_portfolio: Portfolio value, P&L calculation
5. web_search: General finance concepts and definitions
6. get_technical_analysis: RSI, MACD, Moving Averages, signals
7. get_sentiment_analysis: AI sentiment scoring on news articles
8. compare_stocks: Side-by-side comparison of two stocks
9. optimize_portfolio: Modern Portfolio Theory optimization

STRICT RULES:
1. ALWAYS use tools — never answer from memory for market data.
2. For investment questions, use AT LEAST 3 tools:
   price + history + news + technical analysis + sentiment.
3. For Indian stocks use .NS suffix (RELIANCE.NS, TCS.NS, INFY.NS).
4. Always structure responses with clear sections and headers.
5. Always cite which tool provided which data.
6. End every investment recommendation with a risk disclaimer.
7. When comparing stocks, always use compare_stocks tool.
8. When asked about portfolio allocation, use optimize_portfolio tool.
9. Be specific with numbers — never give vague answers.
10. Think step by step before answering complex questions.

You are professional, precise, and always act in the user's best interest."""

# ── 4. Build Agent ───────────────────────────────────────
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT
)

# ── 5. Memory ────────────────────────────────────────────
chat_history = []

def chat(user_message: str) -> str:
    try:
        chat_history.append(HumanMessage(content=user_message))
        result = agent.invoke({"messages": chat_history})
        ai_message = result["messages"][-1]
        response_text = ai_message.content
        chat_history.append(AIMessage(content=response_text))
        return response_text
    except Exception as e:
        return f"Error: {str(e)}"

# ── 6. Test ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("        🤖 FinBot - AI Financial Advisor")
    print("        9 Tools | Real Data | Smart Analysis")
    print("=" * 60)

    test_questions = [
        "Should I buy Apple stock right now? Give me complete analysis.",
        "Compare Reliance and TCS for long term investment.",
    ]

    for question in test_questions:
        print(f"\n👤 User: {question}")
        print("-" * 40)
        answer = chat(question)
        print(f"\n🤖 FinBot: {answer}")
        print("=" * 60)