import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

# Import all 5 tools
from tools.stock_price import get_stock_price
from tools.stock_history import get_stock_history
from tools.financial_news import get_financial_news
from tools.portfolio_analyzer import analyze_portfolio
from tools.web_search import web_search

load_dotenv()

# ── 1. The Brain ─────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# ── 2. All 5 Tools ───────────────────────────────────────
tools = [
    get_stock_price,
    get_stock_history,
    get_financial_news,
    analyze_portfolio,
    web_search
]

# ── 3. System Prompt ─────────────────────────────────────
SYSTEM_PROMPT = """You are FinBot, an expert AI financial advisor with deep 
knowledge of global and Indian stock markets.

You have access to these tools:
- get_stock_price: Get live stock prices
- get_stock_history: Get historical price trends  
- get_financial_news: Get latest news about companies
- analyze_portfolio: Analyze user stock portfolio
- web_search: Search for general finance concepts

RULES:
1. ALWAYS use tools to fetch real data. Never guess prices or news.
2. When asked about a stock, check BOTH price AND news before giving advice.
3. For Indian stocks, tickers end with .NS (RELIANCE.NS, TCS.NS, INFY.NS, WIPRO.NS).
4. Always mention which tool gave you the data.
5. Structure answers clearly with sections.
6. Always end investment advice with a risk disclaimer.
7. Be specific with numbers, never vague."""

# ── 4. Build Agent with LangGraph ────────────────────────
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT
)

# ── 5. Memory (conversation history) ─────────────────────
chat_history = []

def chat(user_message: str) -> str:
    try:
        # Add new user message to history
        chat_history.append(HumanMessage(content=user_message))
        
        # Run agent with full history
        result = agent.invoke({"messages": chat_history})
        
        # Get the last AI message
        ai_message = result["messages"][-1]
        response_text = ai_message.content
        
        # Save AI response to history
        chat_history.append(AIMessage(content=response_text))
        
        return response_text
        
    except Exception as e:
        return f"Error: {str(e)}"


# ── 6. Test ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("        🤖 FinBot - AI Financial Advisor")
    print("=" * 60)

    test_questions = [
        "What is the current price of Apple stock?",
        "How has Tesla performed in the last month?",
        "What is the latest news about Reliance Industries?",
    ]

    for question in test_questions:
        print(f"\n👤 User: {question}")
        print("-" * 40)
        answer = chat(question)
        print(f"\n🤖 FinBot: {answer}")
        print("=" * 60)