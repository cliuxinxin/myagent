import os
import logging
from typing import List, Dict, Any, Optional, Literal
from tools.search_tool import InternetSearchTool

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchAgent:
    """研究代理类"""
    
    def __init__(self, api_key: Optional[str] = None, tavily_api_key: Optional[str] = None, 
                 model_provider: Literal["anthropic", "openai", "deepseek"] = "anthropic"):
        """
        初始化研究代理
        
        Args:
            api_key: 模型提供商的API密钥
            tavily_api_key: Tavily API密钥
            model_provider: 模型提供商 ("anthropic", "openai", "deepseek")
        """
        # 设置API密钥
        self.model_provider = model_provider
        if api_key:
            if model_provider == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = api_key
            elif model_provider == "openai":
                os.environ["OPENAI_API_KEY"] = api_key
            elif model_provider == "deepseek":
                os.environ["DEEPSEEK_API_KEY"] = api_key
        
        if tavily_api_key:
            os.environ["TAVILY_API_KEY"] = tavily_api_key
            
        # 创建搜索工具实例
        self.search_tool = InternetSearchTool()
        
        # 定义系统提示词
        self.system_prompt = """你是一位专业的研究员。你的工作是进行深入的研究并撰写精炼的报告。

你可以使用以下工具来收集信息：

## `internet_search`

使用此工具对给定查询运行互联网搜索。你可以指定要返回的最大结果数、主题以及是否应包含原始内容。

在进行研究时，请遵循以下步骤：
1. 分析用户的问题，确定需要研究的关键点
2. 使用搜索工具收集相关信息
3. 组织和综合信息形成连贯的报告
4. 确保引用所有来源并保持客观性

请以清晰、专业的方式呈现你的发现。"""
        
        # 检查是否可以导入deepagents
        self.deepagents_available = self._check_deepagents_availability()
        if self.deepagents_available:
            try:
                from deepagents import create_deep_agent
                # 根据模型提供商设置相应的模型
                if model_provider == "deepseek":
                    model_name = "deepseek-chat"  # DeepSeek常用模型
                elif model_provider == "anthropic":
                    model_name = "claude-3-opus-20240229"  # Anthropic常用模型
                elif model_provider == "openai":
                    model_name = "gpt-4-turbo"  # OpenAI常用模型
                else:
                    model_name = None
                
                # 创建代理时指定模型
                agent_kwargs = {
                    "tools": [self._internet_search_wrapper],
                    "system_prompt": self.system_prompt
                }
                
                # 如果deepagents支持model参数，则添加
                if model_name:
                    agent_kwargs["model"] = model_name
                    
                self.agent = create_deep_agent(**agent_kwargs)
            except Exception as e:
                logger.warning(f"创建deepagents代理时出错: {e}")
                self.agent = None
        else:
            logger.warning("deepagents库不可用，将使用简化版功能")
            self.agent = None
    
    def _check_deepagents_availability(self) -> bool:
        """检查deepagents库是否可用"""
        try:
            import deepagents
            return True
        except ImportError:
            return False
    
    def _internet_search_wrapper(self, query: str, max_results: int = 5, 
                                topic: Literal["general", "news", "finance"] = "general", 
                                include_raw_content: bool = False) -> Dict[str, Any]:
        """
        互联网搜索工具包装器
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            topic: 主题类型
            include_raw_content: 是否包含原始内容
            
        Returns:
            搜索结果
        """
        return self.search_tool.search(
            query=query,
            max_results=max_results,
            topic=topic,
            include_raw_content=include_raw_content
        )
    
    def research(self, query: str) -> str:
        """
        执行研究任务
        
        Args:
            query: 砠究查询
            
        Returns:
            研究结果
        """
        if self.agent:
            # 使用deepagents代理
            try:
                logger.info(f"使用{self.model_provider}模型研究查询: {query}")
                
                result = self.agent.invoke({
                    "messages": [{"role": "user", "content": query}]
                })
                
                # 返回最后一个消息的内容
                final_content = result["messages"][-1].content
                logger.info("研究完成")
                return final_content
            except Exception as e:
                logger.error(f"使用{self.model_provider}模型代理时发生错误: {str(e)}")
                # 回退到简化版功能
                return self._simple_research(query)
        else:
            # 使用简化版功能
            return self._simple_research(query)
    
    def _simple_research(self, query: str) -> str:
        """
        简化版研究功能（不依赖deepagents）
        
        Args:
            query: 研究查询
            
        Returns:
            研究结果
        """
        try:
            logger.info(f"使用简化版功能研究查询: {query}")
            
            # 执行搜索
            search_result = self.search_tool.get_search_context(query, max_results=5)
            
            # 构造简单的研究报告
            report = f"# 研究报告：{query}\n\n"
            report += "## 搜索结果摘要\n\n"
            report += search_result
            report += f"\n## 结论\n\n"
            report += f"这是基于网络搜索结果的简要报告，使用{self.model_provider}模型提供商。如需更深入的分析，请安装deepagents库以启用高级功能。"
            
            logger.info("简化版研究完成")
            return report
        except Exception as e:
            logger.error(f"简化版研究过程中发生错误: {str(e)}")
            return f"研究失败: {str(e)}"

# 创建代理实例的便捷函数
def create_research_agent(api_key: Optional[str] = None, tavily_api_key: Optional[str] = None, 
                         model_provider: Literal["anthropic", "openai", "deepseek"] = "anthropic") -> ResearchAgent:
    """
    创建研究代理实例
    
    Args:
        api_key: 模型提供商的API密钥
        tavily_api_key: Tavily API密钥
        model_provider: 模型提供商 ("anthropic", "openai", "deepseek")
        
    Returns:
        ResearchAgent实例
    """
    return ResearchAgent(api_key, tavily_api_key, model_provider)