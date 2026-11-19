# Google ADK Project

A collection of small agents built with the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/). Each folder is a standalone agent that shows one capability, from plain web search to a database-backed refund assistant.

## Agents

| Folder | What it demonstrates | Model | Tools |
|---|---|---|---|
| [shiv_bot](shiv_bot) | Basic agent with Google Search grounding | `gemini-3.5-flash` (native) | `google_search` |
| [google_agent](google_agent) | Web-aware agent through OpenRouter's `:online` suffix | Gemini 3.5 Flash via OpenRouter (LiteLLM) | none (search is built into the model route) |
| [tavily_search_agent](tavily_search_agent) | Wrapping a LangChain tool for ADK | Gemini 3.5 Flash via OpenRouter | Tavily search (`LangchainTool`) |
| [world_clock_agent](world_clock_agent) | Custom Python function tool | Gemini 3.5 Flash via OpenRouter | `get_current_time_in_timezone` |
| [code_execution_agent](code_execution_agent) | Writing and running Python to answer questions | Gemini 2.5 Flash via OpenRouter | `BuiltInCodeExecutor` |
| [combined_tool_agent](combined_tool_agent) | Mixing custom, LangChain and built-in tools in one agent | Gemini 3.5 Flash via OpenRouter | clock, Tavily, Google Search, code executor |
| [edtech_refund_agent](edtech_refund_agent) | Multi-step workflow over a SQLite database, with a confirmation step | Gemini 3.5 Flash via OpenRouter | 6 custom tools in [tools.py](edtech_refund_agent/tools.py) |

### Edtech refund agent

The most complete example. It uses sample data in `edtech.db`, and no real money moves. It works like this:

1. Identifies the student by registered email (`identify_student`).
2. Lists their enrollments (`get_my_enrollments`).
3. Checks eligibility (`check_refund_eligibility`).
4. Asks for confirmation, then saves the request (`request_refund`).
5. Reports progress later (`get_refund_status`).

Refund policy: within **7 days** of purchase, at most **20%** of the course completed, active enrollments only, full amount refunded. `get_refund_policy` returns this text.

## Requirements

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/)
- A [Google AI Studio](https://aistudio.google.com/) API key
- An [OpenRouter](https://openrouter.ai/) API key (used by every agent except `shiv_bot`)
- A [Tavily](https://tavily.com/) API key (only for `tavily_search_agent` and `combined_tool_agent`)

## Setup

```bash
# install dependencies into .venv
uv sync
```

Copy the example env file and add your keys. `.env` is git-ignored, so never commit it.

```bash
cp .env.example .env
```

`adk web` and `adk run` also read a `.env` inside an agent folder if one exists.

## Running an agent

Run these from the project root. Each folder name is the agent name ADK uses.

```bash
# web UI: pick an agent from the dropdown
uv run adk web

# terminal chat with one agent
uv run adk run shiv_bot

# API server
uv run adk api_server
```

Example prompts:

- `world_clock_agent`: "What time is it in Mumbai?"
- `code_execution_agent`: "What is the 50th Fibonacci number?"
- `edtech_refund_agent`: "I want a refund. My email is someone@example.com."

## Project layout

```
google-adk-project/
├── shiv_bot/             # Google Search agent
├── google_agent/         # OpenRouter online-search agent
├── tavily_search_agent/  # Tavily via LangChain
├── world_clock_agent/    # custom function tool
├── code_execution_agent/ # built-in code executor
├── combined_tool_agent/  # all tool types together
├── edtech_refund_agent/  # SQLite-backed refund workflow
│   ├── agent.py
│   ├── tools.py
│   └── edtech.db
├── src/google_adk_project/
├── pyproject.toml
└── uv.lock
```

Every agent folder follows the ADK convention: an `agent.py` that defines `root_agent`, plus an `__init__.py`.

## Notes

- `BuiltInCodeExecutor` and the `google_search` tool are Gemini-native. They work best with Gemini models called directly. Through OpenRouter and LiteLLM, behavior can differ, so check the output.
- `combined_tool_agent` sets `include_server_side_tool_invocations=True` so ADK keeps the full context when built-in and custom tools are combined.
- `edtech_refund_agent/edtech.db` is sample data. `request_refund` writes to it, so running the agent shows the file as modified in git. Run `git checkout edtech_refund_agent/edtech.db` to reset it.
