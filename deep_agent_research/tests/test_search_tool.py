import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.search_tool import InternetSearchTool

class TestInternetSearchTool(unittest.TestCase):
    """InternetSearchTool测试类"""
    
    @patch('tools.search_tool.TavilyClient')
    def setUp(self, mock_tavily_client):
        """测试初始化"""
        # 模拟环境变量
        os.environ['TAVILY_API_KEY'] = 'test_key'
        
        # 创建模拟客户端
        self.mock_client_instance = MagicMock()
        mock_tavily_client.return_value = self.mock_client_instance
        
        # 创建搜索工具实例
        self.search_tool = InternetSearchTool()
    
    def test_init_with_api_key(self):
        """测试使用API密钥初始化"""
        search_tool = InternetSearchTool(api_key='test_key')
        self.assertEqual(search_tool.api_key, 'test_key')
    
    @patch.dict(os.environ, {'TAVILY_API_KEY': 'env_key'})
    def test_init_with_env_key(self):
        """测试从环境变量获取API密钥"""
        search_tool = InternetSearchTool()
        self.assertEqual(search_tool.api_key, 'env_key')
    
    def test_init_without_api_key(self):
        """测试没有API密钥时抛出异常"""
        # 临时删除环境变量
        if 'TAVILY_API_KEY' in os.environ:
            del os.environ['TAVILY_API_KEY']
        
        with self.assertRaises(ValueError):
            InternetSearchTool()
        
        # 恢复环境变量
        os.environ['TAVILY_API_KEY'] = 'test_key'
    
    @patch('tools.search_tool.TavilyClient')
    def test_search_success(self, mock_tavily_client):
        """测试搜索成功"""
        # 设置模拟返回值
        mock_result = {
            'results': [
                {'title': 'Test Result 1', 'url': 'http://test1.com', 'content': 'Content 1'},
                {'title': 'Test Result 2', 'url': 'http://test2.com', 'content': 'Content 2'}
            ]
        }
        
        mock_client_instance = MagicMock()
        mock_tavily_client.return_value = mock_client_instance
        mock_client_instance.search.return_value = mock_result
        
        # 创建搜索工具实例
        search_tool = InternetSearchTool(api_key='test_key')
        
        # 执行搜索
        result = search_tool.search('test query')
        
        # 验证结果
        self.assertEqual(result, mock_result)
        mock_client_instance.search.assert_called_once_with(
            'test query',
            max_results=5,
            topic='general',
            include_raw_content=False,
            search_depth='basic'
        )
    
    @patch('tools.search_tool.TavilyClient')
    def test_search_with_parameters(self, mock_tavily_client):
        """测试带参数的搜索"""
        mock_client_instance = MagicMock()
        mock_tavily_client.return_value = mock_client_instance
        mock_client_instance.search.return_value = {'results': []}
        
        # 创建搜索工具实例
        search_tool = InternetSearchTool(api_key='test_key')
        
        # 执行带参数的搜索
        search_tool.search(
            query='test query',
            max_results=10,
            topic='news',
            include_raw_content=True,
            search_depth='advanced'
        )
        
        # 验证调用参数
        mock_client_instance.search.assert_called_once_with(
            'test query',
            max_results=10,
            topic='news',
            include_raw_content=True,
            search_depth='advanced'
        )
    
    @patch('tools.search_tool.TavilyClient')
    def test_search_exception(self, mock_tavily_client):
        """测试搜索异常处理"""
        mock_client_instance = MagicMock()
        mock_tavily_client.return_value = mock_client_instance
        mock_client_instance.search.side_effect = Exception('API Error')
        
        # 创建搜索工具实例
        search_tool = InternetSearchTool(api_key='test_key')
        
        # 验证异常被正确传播
        with self.assertRaises(Exception) as context:
            search_tool.search('test query')
        
        self.assertIn('API Error', str(context.exception))
    
    @patch('tools.search_tool.TavilyClient')
    def test_get_search_context(self, mock_tavily_client):
        """测试获取搜索上下文"""
        # 设置模拟返回值
        mock_result = {
            'results': [
                {'title': 'Test Title 1', 'url': 'http://test1.com', 'content': 'Test Content 1'},
                {'title': 'Test Title 2', 'url': 'http://test2.com', 'content': 'Test Content 2'}
            ]
        }
        
        mock_client_instance = MagicMock()
        mock_tavily_client.return_value = mock_client_instance
        mock_client_instance.search.return_value = mock_result
        
        # 创建搜索工具实例
        search_tool = InternetSearchTool(api_key='test_key')
        
        # 获取搜索上下文
        context = search_tool.get_search_context('test query', max_results=2)
        
        # 验证结果包含关键信息
        self.assertIn('test query', context)
        self.assertIn('Test Title 1', context)
        self.assertIn('Test Title 2', context)
        self.assertIn('http://test1.com', context)
        self.assertIn('http://test2.com', context)

if __name__ == '__main__':
    unittest.main()