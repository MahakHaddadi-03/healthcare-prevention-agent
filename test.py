# from dotenv import load_dotenv
# from langchain_groq import ChatGroq
# from pydantic import BaseModel
# from typing import Optional
# import os

# load_dotenv()

# class Person(BaseModel):
#     name: Optional[str] = None
#     age: Optional[int] = None

# llm = ChatGroq(
#     model="llama-3.1-8b-instant",
#     api_key=os.getenv("GROQ_API_KEY"),
#     temperature=0,
# )

# structured = llm.with_structured_output(Person)

# result = structured.invoke("My name is John. I am 23 years old.")

# print(result)