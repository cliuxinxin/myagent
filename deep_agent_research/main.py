#!/usr/bin/env python3
"""
研究代理主应用程序
这是一个示例应用程序，展示如何使用研究代理执行研究任务。
"""

import os
import sys
import argparse
import logging
from typing import Optional

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from agents.research_agent import create_research_agent
from utils.config import get_env_variable, load_environment_variables

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    # 加载环境变量
    load_environment_variables()
    
    parser = argparse.ArgumentParser(description="研究代理应用程序")
    parser.add_argument(
        "--query", 
        type=str, 
        help="研究查询",
        default="What is LangGraph?"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="模型提供商API密钥",
        default=None
    )
    parser.add_argument(
        "--tavily-key",
        type=str,
        help="Tavily API密钥",
        default=get_env_variable("TAVILY_API_KEY")
    )
    parser.add_argument(
        "--model-provider",
        type=str,
        choices=["anthropic", "openai", "deepseek"],
        help="模型提供商",
        default="deepseek"
    )
    
    args = parser.parse_args()
    
    # 获取API密钥
    api_key = args.api_key
    if not api_key:
        if args.model_provider == "anthropic":
            api_key = get_env_variable("ANTHROPIC_API_KEY")
        elif args.model_provider == "openai":
            api_key = get_env_variable("OPENAI_API_KEY")
        elif args.model_provider == "deepseek":
            api_key = get_env_variable("DEEPSEEK_API_KEY")
    
    # 检查API密钥
    if not api_key:
        logger.error(f"缺少{args.model_provider} API密钥。请通过--api-key参数或相应的环境变量提供。")
        return 1
        
    if not args.tavily_key:
        logger.error("缺少Tavily API密钥。请通过--tavily-key参数或TAVILY_API_KEY环境变量提供。")
        return 1
    
    try:
        # 创建研究代理
        logger.info(f"正在初始化研究代理，使用{args.model_provider}模型...")
        agent = create_research_agent(
            api_key=api_key,
            tavily_api_key=args.tavily_key,
            model_provider=args.model_provider
        )
        
        # 执行研究
        logger.info(f"正在研究查询: {args.query}")
        result = agent.research(args.query)
        
        # 输出结果
        print("=" * 80)
        print("研究结果:")
        print("=" * 80)
        print(result)
        print("=" * 80)
        
        return 0
    except Exception as e:
        logger.error(f"应用程序执行出错: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())