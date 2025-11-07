"""
deep_research_agent/main.py

Deep Agent example using DeepSeek model with subagents for delegated research tasks.
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
# Step 2: Initialize Tavily search client
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
# Step 3: Define subagents
# -----------------------------
deep_research_subagent = {
    "name": "deep-researcher",
    "model": "deepseek-chat",
    "description": (
        "Conducts in-depth, multi-step research using the internet_search tool. "
        "Use when the question requires synthesis from multiple sources."
    ),
    "system_prompt": """You are a specialized research subagent.

Your task:
1. Break down complex research questions into specific, searchable queries.
2. Use the internet_search tool for each query.
3. Synthesize findings into a concise, structured report.

Output format:
- Executive Summary (2–3 paragraphs)
- Key Findings (bullet points)
- Source List (URLs only)

Constraints:
- Keep under 500 words.
- Do NOT include raw tool output or unnecessary details.""",
    "tools": [internet_search],
}

quick_lookup_subagent = {
    "name": "quick-lookup",
    "model": "deepseek-chat",
    "description": (
        "Handles short factual or definition-style queries. "
        "Use when the user asks for a simple explanation or definition."
    ),
    "system_prompt": """You are a concise assistant.

Provide brief, accurate answers to factual questions.
Use internet_search only when necessary.
Limit response to 150 words.""",
    "tools": [internet_search],
}

subagents = [deep_research_subagent, quick_lookup_subagent]

# -----------------------------
# Step 4: Define system instructions for main agent
# -----------------------------
research_instructions = """You are an expert research coordinator using the DeepSeek model.

Your role:
- Plan and oversee research projects.
- Delegate complex or multi-step research tasks to subagents using the task() tool.
- Use subagents to maintain clean context and concise final outputs.

Available subagents:
- deep-researcher: for in-depth, multi-source research.
- quick-lookup: for short factual lookups.
"""

# -----------------------------
# Step 5: Create the main agent
# -----------------------------
agent = create_deep_agent(
    model="deepseek-chat",
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=subagents,
)

# -----------------------------
# Step 6: Run the agent
# -----------------------------
if __name__ == "__main__":
    query = "荷兰安世半导体纠纷问题是怎么回事？"
    print(f"🔍 Running delegated research on: {query}\n")

    result = agent.invoke({"messages": [{"role": "user", "content": query}]})

    print("📘 Agent Report:\n")
    print(result["messages"][-1].content)
