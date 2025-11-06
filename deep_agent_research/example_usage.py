#!/usr/bin/env python3
"""
研究代理使用示例
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.research_agent import create_research_agent

def main():
    """示例主函数"""
    print("研究代理使用示例")
    print("=" * 50)
    
    # 检查API密钥
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        print("警告：未找到TAVILY_API_KEY环境变量")
        print("请设置TAVILY_API_KEY环境变量以获得完整的功能")
        print("示例：export TAVILY_API_KEY=your_api_key_here")
        return
    
    try:
        # 创建研究代理
        print("正在创建研究代理...")
        agent = create_research_agent(tavily_api_key=tavily_key)
        
        # 检查代理是否成功创建
        if not agent.agent:
            print("警告：deepagents库未安装，功能受限")
            print("请安装deepagents以获得完整功能：pip install deepagents")
            return
        
        # 执行研究
        query = "What is LangGraph and what are its main features?"
        print(f"\n正在研究查询: {query}")
        print("-" * 50)
        
        result = agent.research(query)
        print("研究结果:")
        print(result)
        
    except Exception as e:
        print(f"执行过程中出现错误: {str(e)}")
        print("请确保已正确安装所有依赖项")

if __name__ == "__main__":
    main()