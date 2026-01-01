import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

_llm = None


def get_base_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    return _llm
