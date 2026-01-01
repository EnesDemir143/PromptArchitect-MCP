import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()

_llm = None


def get_base_llm():
    global _llm
    if _llm is None:
        provider = os.getenv("LLM_PROVIDER", "openai").lower()

        if provider == "openai":
            _llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        elif provider == "gemini":
            _llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
            )
        elif provider == "anthropic":
            _llm = ChatAnthropic(
                model="claude-3-5-sonnet-latest",
                temperature=0,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    return _llm
