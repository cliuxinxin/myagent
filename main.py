"""
deep_research_agent/main.py

Deep Agent example using DeepSeek model and LangSmith tracing
(compatible with current deepagents versions).
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

# -----------------------------
# Step 3: Initialize Tavily search client
# -----------------------------
tavily_client = TavilyClient()

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search via Tavily."""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

# -----------------------------
# Step 4: Define system instructions
# -----------------------------
research_instructions = """You are an expert researcher using the DeepSeek model.
Conduct thorough investigations and produce concise, well-structured reports.

You may use the following tool:
- internet_search(query, max_results=5, topic='general'): Search the web for relevant information.
"""

# -----------------------------
# Step 5: Create the agent
# -----------------------------
agent = create_deep_agent(
    model="deepseek-chat",  # Use DeepSeek via OpenAI API
    tools=[internet_search],
    system_prompt=research_instructions,
)

# -----------------------------
# Step 6: Run the agent
# -----------------------------
if __name__ == "__main__":
    query = "What is LangGraph?"
    print(f"🔍 Running research on: {query}\n")

    result = agent.invoke({"messages": [{"role": "user", "content": query}]})

    print("📘 Agent Report:\n")
    print(result["messages"][-1].content)
