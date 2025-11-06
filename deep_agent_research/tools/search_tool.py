import os
from typing import Literal, Optional, List, Dict, Any
from tavily import TavilyClient
import logging

# 配置日志
logger = logging.getLogger(__name__)

class InternetSearchTool:
    """互联网搜索工具类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化搜索工具
        
        Args:
            api_key: Tavily API密钥，如果未提供则从环境变量获取
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        self.client = TavilyClient(api_key=self.api_key)
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
        search_depth: Literal["basic", "advanced"] = "basic"
    ) -> Dict[str, Any]:
        """
        执行网络搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            topic: 搜索主题类型
            include_raw_content: 是否包含原始内容
            search_depth: 搜索深度
            
        Returns:
            搜索结果字典
        """
        try:
            logger.info(f"执行搜索查询: {query}")
            result = self.client.search(
                query,
                max_results=max_results,
                topic=topic,
                include_raw_content=include_raw_content,
                search_depth=search_depth
            )
            logger.info(f"搜索完成，返回 {len(result.get('results', []))} 个结果")
            return result
        except Exception as e:
            logger.error(f"搜索过程中发生错误: {str(e)}")
            raise
    
    def get_search_context(self, query: str, max_results: int = 3) -> str:
        """
        获取搜索结果的文本上下文
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            
        Returns:
            格式化的搜索结果文本
        """
        try:
            result = self.search(query, max_results=max_results)
            context = f"搜索查询: {query}\n\n"
            
            for i, item in enumerate(result.get('results', []), 1):
                context += f"{i}. {item.get('title', 'N/A')}\n"
                context += f"   URL: {item.get('url', 'N/A')}\n"
                context += f"   内容: {item.get('content', 'N/A')}\n\n"
            
            return context
        except Exception as e:
            logger.error(f"获取搜索上下文时发生错误: {str(e)}")
            return f"无法获取搜索结果: {str(e)}"