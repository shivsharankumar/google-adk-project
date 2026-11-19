
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
# from google.genai import types
from google.adk.tools.google_search_tool import google_search
from google.adk.code_executors import BuiltInCodeExecutor,UnsafeLocalCodeExecutor
from dotenv import load_dotenv
import os
load_dotenv()

root_agent = Agent(
    model=LiteLlm(
        model="openrouter/google/gemini-2.5-flash",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        api_base="https://openrouter.ai/api/v1",
    ),
    name="root_agent",
    description="A helpful assistant that can write and run python code",
    instruction=(
        "Answer user questions accurately. "
        "when a question involves calculations, data analysis,or anything "
        "that benefits from running code ,write python and execute it,"
        "then explain the result"
    ),
    code_executor=BuiltInCodeExecutor(),
)
