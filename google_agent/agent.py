
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
# from google.genai import types
from google.adk.tools.google_search_tool import google_search
from dotenv import load_dotenv
import os
load_dotenv()

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
        "Use current web information when needed and verify facts."
    ),
)
