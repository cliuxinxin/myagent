"""
A minimal example of building a Deep Agent using DeepSeek as the model backend,
with support for subagents.
"""

from langgraph.graph.state import CompiledStateGraph


import os
from typing import Any, Literal
from dotenv import load_dotenv
from tavily import TavilyClient
from deepagents import create_deep_agent

# -----------------------------
# Step 1: Load environment variables
# -----------------------------
load_dotenv()
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
    """Run a web search via Tavily API."""
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
你是一个专业的研究助手。

重要:对于复杂的研究任务,使用task()工具委派给你的subagent。
这样可以保持你的上下文清晰并提高结果质量。

当遇到需要多步骤研究的问题时,委派给research-agent subagent。
"""

# -----------------------------
# Step 4: Define subagents
# -----------------------------
research_subagent = {
       "name": "research-agent",
    "description": "用于深入研究复杂问题,需要多次搜索和综合分析时使用。适合需要详细调查的主题。",  # 更具体
    "system_prompt": """你是一个专业的研究员。你的工作是:
1. 将研究问题分解为可搜索的查询
2. 使用internet_search查找相关信息
3. 综合发现并给出简洁总结
4. 引用来源

输出格式:
- 摘要(2-3段)
- 关键发现(要点)
- 来源(带URL)

保持回复在500字以内。""",
    "tools": [internet_search],
    "model": "deepseek-chat",
}

subagents = [research_subagent]

# -----------------------------
# Step 5: Create the deep agent with subagents
# -----------------------------
agent: CompiledStateGraph[Any, None, Any, Any] = create_deep_agent(
    system_prompt=research_instructions,
    model="deepseek-chat",
    subagents=subagents
)

# -----------------------------
# Step 6: Run the agent
# -----------------------------
if __name__ == "__main__":
    query = "总结一下荷兰安世夺权的这个事情。"
    print(f"🧭 Running research query: {query}\n")

    for step in agent.stream(
            {"messages": [{"role": "user", "content": query}]},
            stream_mode="values",
            subgraphs=True  # 添加这个参数
        ):
            namespace, data = step  # 解包元组
            latest_message = data["messages"][-1]
            
                # 解析并显示更友好的名称
            if namespace:
                node_info = namespace[-1]  # 获取最后一层
                node_name = node_info.split(":")[0]  # 提取节点名称
                print(f"\n[{node_name}]")
            else:
                print(f"\n[Main Agent]")
            
            print(f"{latest_message.type}: {latest_message.content}")
