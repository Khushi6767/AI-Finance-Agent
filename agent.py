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

groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise ValueError("GROQ_API_KEY not found.")

# ── 1. Brain ─────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=groq_key
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
SYSTEM_PROMPT = """You are FinBot, an elite AI financial advisor.

CRITICAL RULE: You MUST use tools for EVERY financial question.
NEVER answer from memory. NEVER say "based on available data".
If a tool fails, try again with a simpler input.

For ANY stock question you MUST call these tools in order:
1. get_stock_price with just the ticker like HDFCBANK.NS
2. get_stock_history with input like HDFCBANK.NS 1mo
3. get_financial_news with company name like HDFC Bank
4. get_technical_analysis with input like HDFCBANK.NS 3mo

You have these 9 tools:
1. get_stock_price - input: ticker symbol like AAPL or HDFCBANK.NS
2. get_stock_history - input: TICKER PERIOD like AAPL 1mo
3. get_financial_news - input: company name like Apple or HDFC Bank
4. analyze_portfolio - input: TICKER:SHARES:PRICE format
5. web_search - input: search query string
6. get_technical_analysis - input: TICKER PERIOD like AAPL 3mo
7. get_sentiment_analysis - input: company name like Apple
8. compare_stocks - input: TICKER1 TICKER2 like AAPL MSFT
9. optimize_portfolio - input: TICKER1,TICKER2,TICKER3

User risk profile is stored in memory - use it to tailor advice.
Always end with risk disclaimer.
Always cite which tool gave which data."""

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