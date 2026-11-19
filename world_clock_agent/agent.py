from google.adk.agents.llm_agent import Agent
from datetime import datetime
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError
from google.adk.models.lite_llm import LiteLlm
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
        "You tell users the current time and date in any city or country. "
        "Translate place names into IANA timezone yourself (eg. Mumbai -> Asia/Kolkata). "
        "and call the get_current_time_in_timezone function to get the current time. "
        "if it returns status 'error' explain the error explain the problem  "
        "and ask the user to clarify."
        ),
    tools=[get_current_time_in_timezone]
)
