from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
# from google.genai import types
from google.adk.tools.google_search_tool import google_search
from dotenv import load_dotenv
import os
load_dotenv()

root_agent = Agent(
    # model=LiteLlm(
    #     model="openrouter/google/gemini-3.5-flash",
    #     api_key=os.getenv("OPENROUTER_API_KEY"),
    #     api_base="https://openrouter.ai/api/v1",
    #     ),
    model="gemini-3.5-flash",
    name='root_agent',
    # description='A helpful assistant for user questions.',
    description='A helpful assistant that can search the web',
    instruction=(
    "Answer user questions accurately. "
    "Use Google search when you need current information "
    "or need to verify facts."
),
    # generate_content_config=types.GenerateContentConfig(
    #     temperature=0.3,
    #     max_output_tokens=800
    # )
    tools=[google_search]

)
