import os
import ssl
from typing import Literal

from tavily import TavilyClient
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, AIMessageChunk

_default_ssl_context = ssl.create_default_context

def _tls12_default_context(*args, **kwargs):
    ctx = _default_ssl_context(*args, **kwargs)
    if hasattr(ssl, "TLSVersion"):
        ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    return ctx

ssl.create_default_context = _tls12_default_context


def _load_env_file(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def _iter_text_parts(content):
    if isinstance(content, str):
        yield content
    elif isinstance(content, dict):
        text = content.get("text")
        if isinstance(text, str) and content.get("type", "text") == "text":
            yield text
        for key in ("content", "value", "delta"):
            if key in content:
                yield from _iter_text_parts(content[key])
    elif isinstance(content, (list, tuple)):
        for part in content:
            yield from _iter_text_parts(part)

_load_env_file()

# Initialize Tavily client
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

# System prompt to steer the agent to be an expert researcher
research_instructions = """You are an expert researcher.
Your job is to conduct thorough research and then write a polished report.
You have access to an internet search tool as your primary means of gathering information.

## `internet_search`
Use this to run an internet search for a given query.
You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

# 
llm = init_chat_model(
        model=os.environ["ANTHROPIC_MODEL"],
        model_provider="anthropic",
        api_key=os.environ["ANTHROPIC_API_KEY"],
        base_url=os.environ["ANTHROPIC_BASE_URL"],
        temperature=0.2,
    )

# Create the deep agent
agent = create_deep_agent(
    model=llm,
    tools=[internet_search],
    system_prompt=research_instructions,
)

# Run the agent
if __name__ == "__main__":
    streamed = False
    final_content = None
    for message, _metadata in agent.stream(
        {"messages": [{"role": "user", "content": "langgraph?是什么"}]},
        stream_mode="messages",
    ):
        if isinstance(message, AIMessageChunk):
            for text in _iter_text_parts(message.content):
                streamed = True
                print(text, end="", flush=True)
        elif isinstance(message, AIMessage):
            final_content = message.content
    if not streamed and final_content:
        for text in _iter_text_parts(final_content):
            print(text, end="")
    print()
