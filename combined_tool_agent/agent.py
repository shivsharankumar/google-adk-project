from google.adk.agents.llm_agent import Agent
from datetime import datetime
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.google_search_tool import google_search
from google.adk.tools.langchain_tool import LangchainTool
from langchain_tavily import TavilySearch
from google.genai import types
from google.adk.code_executors import BuiltInCodeExecutor,UnsafeLocalCodeExecutor
from dotenv import load_dotenv
import os
load_dotenv()
def get_current_time_in_timezone(timezone: str) -> dict:
    """
    Get the current time in a specified timezone.

    Args:
        timezone (str): The timezone for which to get the current time.
        eg: "America/New_York", "Europe/London", "Asia/Tokyo"
    Returns:
        dict: A dictionary containing the current time in the specified timezone.
    """
    try:
        # Get the current time in the specified timezone
        current_time = datetime.now(ZoneInfo(timezone))
        # return {
        #     "timezone": timezone,
        #     "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S")
        # }
    except ZoneInfoNotFoundError:
        return {
            "status": "error",
            "error_message": f"Invalid timezone: {timezone}. Please provide a valid timezone."
        }
    
    return {
        "status": "success",
        "timezone": timezone,
        "date": current_time.strftime("%Y-%m-%d"),
        "time": current_time.strftime("%H:%M:%S"),
        "weekday": current_time.strftime("%A"),
    }

#1 create a TavilySearch instance
tavily_search = TavilySearch(
    max_results=5,
    topic="general"
)
tavily_tool=LangchainTool(tool=tavily_search)

root_agent = Agent(
    # model='gemini-3.5-flash',
    model=LiteLlm(
            model="openrouter/google/gemini-3.5-flash:online",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            api_base="https://openrouter.ai/api/v1",
        ),
    name='clock_agent',
    description='Tells the current time and date anywhere in the world',
    instruction=(
    "Answer user questions accurately.\n"
    "- Use Google Search for current information and quick fact checks.\n"
    "- Use the Tavily search tool when you need more detailed results,"
    "multiple sources, or when Google Search did not give enough.\n"
    "- Write and run Python code for calculations or data analysis.\n"
    "- Use get_current_time whenever the user asks for the time or date"
    "somewhere. Never guess the current time.\n"
    "Cite sources when you use search results."
),
    tools=[get_current_time_in_timezone,tavily_tool,google_search],
    code_executor=BuiltInCodeExecutor(),
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(include_server_side_tool_invocations=True),
    )#here we will use only for built in tools.it is saying it must have complete context to the adk.
)
