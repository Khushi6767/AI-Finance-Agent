import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

if __name__ == "__main__":
    print("Testing Groq connection...")
    response = llm.invoke("What is a stock market in one sentence?")
    print("AI Response:", response.content)
    print("\n✅ Groq LLM is working correctly!")