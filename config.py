from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import os

# load_dotenv()
# llm = ChatOpenAI(
#     model="google/gemma-4-26b-a4b-it:free",
#     api_key=os.getenv("OPENROUTER_API_KEY"),
#     base_url="https://openrouter.ai/api/v1",
#     temperature=0,
# )

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY")
)
