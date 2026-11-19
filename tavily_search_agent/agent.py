
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
# from google.genai import types
from google.adk.tools.langchain_tool import LangchainTool
from langchain_tavily import TavilySearch
from google.adk.tools.google_search_tool import google_search
from dotenv import load_dotenv
import os
load_dotenv()

#1 create a TavilySearch instance
tavily_search = TavilySearch(
    max_results=5,
    topic="general"
)
tavily_tool=LangchainTool(tool=tavily_search)

root_agent = Agent(
    model=LiteLlm(
        model="openrouter/google/gemini-3.5-flash:online",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        api_base="https://openrouter.ai/api/v1",
    ),
    name="root_agent",
    description="A helpful assistant that can search the web",
    instruction=(
        "Answer user questions accurately. "
        "use the tavily search tool when you need current information "
        "or need to verify facts."
    ),
    tools=[tavily_tool]
)
