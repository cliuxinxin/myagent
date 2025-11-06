"""
deep_research_agent/main.py

A minimal example of building a Deep Agent using DeepSeek as the model backend.
"""

import os
from typing import Literal

from dotenv import load_dotenv
from tavily import TavilyClient
from deepagents import create_deep_agent


# -----------------------------
# Step 1: Load environment variables
# -----------------------------
load_dotenv()

# Load keys from .env
tavily_api_key = os.getenv("TAVILY_API_KEY")

# -----------------------------
# Step 2: Initialize Tavily client
# -----------------------------
tavily_client = TavilyClient(api_key=tavily_api_key)


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """
    Run a web search via Tavily API.

    Parameters
    ----------
    query : str
        The search query.
    max_results : int, optional
        Maximum number of results to return.
    topic : Literal["general", "news", "finance"], optional
        Category of the search.
    include_raw_content : bool, optional
        Whether to include raw content in the response.

    Returns
    -------
    dict
        Search results from Tavily.
    """
    return tavily_client.search(
        query=query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


# -----------------------------
# Step 3: Define research instructions
# -----------------------------
research_instructions = """
You are an expert research assistant.
Your duties include conducting thorough research and composing polished reports.

## Tools
You can use `internet_search` to find information online.
Each query may specify a topic category, number of results, and whether to include raw content.
"""

# -----------------------------
# Step 4: Create the deep agent
# -----------------------------
agent = create_deep_agent(
    tools=[internet_search],
    system_prompt=research_instructions,
    model="deepseek-chat",  # Explicitly select DeepSeek model
)

# -----------------------------
# Step 5: Run the agent
# -----------------------------
if __name__ == "__main__":
    query = "What is LangGraph?"
    print(f"🧭 Running research query: {query}\n")

    result = agent.invoke({"messages": [{"role": "user", "content": query}]})

    final_message = result["messages"][-1].content
    print("📘 Research Report:\n")
    print(final_message)
