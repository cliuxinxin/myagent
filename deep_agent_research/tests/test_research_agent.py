import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.research_agent import ResearchAgent, create_research_agent

class TestResearchAgent(unittest.TestCase):
    """ResearchAgent测试类"""
    
    @patch('agents.research_agent.InternetSearchTool')
    def setUp(self, mock_search_tool):
        """测试初始化"""
        # 创建模拟搜索工具
        self.mock_search_tool_instance = MagicMock()
        mock_search_tool.return_value = self.mock_search_tool_instance
        
        # 创建研究代理实例
        self.agent = ResearchAgent(
            anthropic_api_key='test_anthropic_key',
            tavily_api_key='test_tavily_key'
        )
    
    @patch('agents.research_agent.InternetSearchTool')
    @patch('agents.research_agent.create_deep_agent')
    def test_init_success(self, mock_create_deep_agent, mock_search_tool):
        """测试成功初始化"""
        # 创建模拟对象
        mock_search_tool_instance = MagicMock()
        mock_search_tool.return_value = mock_search_tool_instance
        mock_agent_instance = MagicMock()
        mock_create_deep_agent.return_value = mock_agent_instance
        
        # 创建代理
        agent = ResearchAgent(
            anthropic_api_key='test_anthropic_key',
            tavily_api_key='test_tavily_key'
        )
        
        # 验证
        self.assertEqual(agent.search_tool, mock_search_tool_instance)
        self.assertEqual(agent.agent, mock_agent_instance)
    
    @patch('agents.research_agent.InternetSearchTool')
    @patch('agents.research_agent.create_deep_agent')
    def test_init_without_deepagents(self, mock_create_deep_agent, mock_search_tool):
        """测试在没有deepagents时初始化"""
        # 模拟导入错误
        mock_create_deep_agent.side_effect = ImportError("deepagents not found")
        
        # 创建模拟搜索工具
        mock_search_tool_instance = MagicMock()
        mock_search_tool.return_value = mock_search_tool_instance
        
        # 创建代理
        agent = ResearchAgent(
            anthropic_api_key='test_anthropic_key',
            tavily_api_key='test_tavily_key'
        )
        
        # 验证
        self.assertEqual(agent.search_tool, mock_search_tool_instance)
        self.assertIsNone(agent.agent)
    
    @patch('agents.research_agent.InternetSearchTool')
    def test_internet_search_wrapper(self, mock_search_tool):
        """测试互联网搜索包装器"""
        # 设置模拟返回值
        mock_result = {'results': [{'title': 'Test', 'url': 'http://test.com', 'content': 'Test content'}]}
        self.mock_search_tool_instance.search.return_value = mock_result
        
        # 调用包装器
        result = self.agent._internet_search_wrapper('test query')
        
        # 验证
        self.assertEqual(result, mock_result)
        self.mock_search_tool_instance.search.assert_called_once_with(
            query='test query',
            max_results=5,
            topic='general',
            include_raw_content=False
        )
    
    @patch('agents.research_agent.InternetSearchTool')
    @patch('agents.research_agent.create_deep_agent')
    def test_research_success(self, mock_create_deep_agent, mock_search_tool):
        """测试研究成功"""
        # 创建模拟对象
        mock_search_tool_instance = MagicMock()
        mock_search_tool.return_value = mock_search_tool_instance
        
        mock_agent_instance = MagicMock()
        mock_create_deep_agent.return_value = mock_agent_instance
        
        # 设置模拟返回值
        mock_result = {
            "messages": [
                {"role": "user", "content": "What is LangGraph?"},
                {"role": "assistant", "content": "LangGraph is a library for building stateful, multi-actor applications with LLMs."}
            ]
        }
        mock_agent_instance.invoke.return_value = mock_result
        
        # 创建代理
        agent = ResearchAgent(
            anthropic_api_key='test_anthropic_key',
            tavily_api_key='test_tavily_key'
        )
        
        # 执行研究
        result = agent.research("What is LangGraph?")
        
        # 验证
        self.assertEqual(result, "LangGraph is a library for building stateful, multi-actor applications with LLMs.")
        mock_agent_instance.invoke.assert_called_once()
    
    @patch('agents.research_agent.InternetSearchTool')
    @patch('agents.research_agent.create_deep_agent')
    def test_research_without_agent(self, mock_create_deep_agent, mock_search_tool):
        """测试在没有代理时的研究功能"""
        # 模拟导入错误
        mock_create_deep_agent.side_effect = ImportError("deepagents not found")
        
        # 创建模拟搜索工具
        mock_search_tool_instance = MagicMock()
        mock_search_tool.return_value = mock_search_tool_instance
        
        # 创建代理
        agent = ResearchAgent(
            anthropic_api_key='test_anthropic_key',
            tavily_api_key='test_tavily_key'
        )
        
        # 执行研究
        result = agent.research("What is LangGraph?")
        
        # 验证
        self.assertEqual(result, "错误：deepagents库未安装，无法执行研究任务。")
    
    @patch('agents.research_agent.InternetSearchTool')
    @patch('agents.research_agent.create_deep_agent')
    def test_research_exception(self, mock_create_deep_agent, mock_search_tool):
        """测试研究异常处理"""
        # 创建模拟对象
        mock_search_tool_instance = MagicMock()
        mock_search_tool.return_value = mock_search_tool_instance
        
        mock_agent_instance = MagicMock()
        mock_create_deep_agent.return_value = mock_agent_instance
        
        # 模拟异常
        mock_agent_instance.invoke.side_effect = Exception("Agent error")
        
        # 创建代理
        agent = ResearchAgent(
            anthropic_api_key='test_anthropic_key',
            tavily_api_key='test_tavily_key'
        )
        
        # 执行研究
        result = agent.research("What is LangGraph?")
        
        # 验证
        self.assertIn("研究失败", result)
        self.assertIn("Agent error", result)
    
    def test_create_research_agent(self):
        """测试创建研究代理的便捷函数"""
        with patch.object(ResearchAgent, '__init__', return_value=None):
            agent = create_research_agent(
                anthropic_api_key='test_anthropic_key',
                tavily_api_key='test_tavily_key'
            )
            
            # 验证返回类型
            self.assertIsInstance(agent, ResearchAgent)

if __name__ == '__main__':
    unittest.main()