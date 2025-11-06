# 深度智能研究代理

这是一个基于deepagents框架构建的智能研究代理，能够执行网络搜索、信息收集和报告生成任务。

## 功能特性

- 网络搜索能力（使用Tavily API）
- 自动研究规划（需要deepagents）
- 信息综合与报告生成
- 模块化设计，易于扩展
- 两种运行模式：
  - 完整模式（安装deepagents后）：具备完整的AI代理能力
  - 简化模式（仅依赖tavily-python）：基础搜索和报告功能

## 安装依赖

### 完整功能安装（推荐）

```bash
pip install -r requirements.txt
pip install deepagents
```

或者使用uv:

```bash
uv add deepagents tavily-python
```

或者使用poetry:

```bash
poetry add deepagents tavily-python
```

### 基础功能安装

如果只需要基础功能，可以只安装基础依赖：

```bash
pip install tavily-python python-dotenv
```

## 环境配置

1. 复制示例配置文件：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入您的API密钥：
   ```bash
   TAVILY_API_KEY=your_tavily_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## 使用方法

### 命令行使用

```bash
python main.py --query "What is LangGraph?"
```

或者指定API密钥：

```bash
python main.py --query "What is LangGraph?" --tavily-key "your-tavily-key" --anthropic-key "your-anthropic-key"
```

### 示例脚本使用

```bash
python example_usage.py
```

### 作为模块使用

```python
from agents.research_agent import create_research_agent

# 创建代理
agent = create_research_agent(
    tavily_api_key="your-tavily-key",
    anthropic_api_key="your-anthropic-key"
)

# 执行研究
result = agent.research("What is LangGraph?")
print(result)
```

## 运行测试

要运行所有测试：

```bash
python run_tests.py
```

或者使用unittest模块：

```bash
python -m unittest discover tests
```

## 功能差异说明

| 功能 | 完整模式 (含deepagents) | 简化模式 (仅tavily) |
|------|------------------------|-------------------|
| 网络搜索 | ✅ | ✅ |
| AI规划 | ✅ | ❌ |
| 上下文管理 | ✅ | ❌ |
| 子代理委派 | ✅ | ❌ |
| 报告生成 | ✅ (AI增强) | ✅ (基础格式) |

## 项目结构

```
deep_agent_research/
├── agents/                 # 代理实现
│   └── research_agent.py   # 研究代理
├── tools/                  # 工具实现
│   └── search_tool.py      # 搜索工具
├── utils/                  # 工具函数
├── tests/                  # 测试文件
├── main.py                 # 主应用程序
├── example_usage.py        # 使用示例
├── requirements.txt        # 依赖列表
├── setup.py                # 安装脚本
├── .env.example            # 环境变量示例
└── README.md               # 说明文档
```

## 开发指南

### 添加新工具

1. 在 `tools/` 目录中创建新工具文件
2. 实现工具功能
3. 在 `agents/research_agent.py` 中注册工具

### 扩展代理功能

1. 修改系统提示词以调整代理行为
2. 添加新的工具函数
3. 调整代理配置参数

## 故障排除

### ImportError: No module named 'deepagents'

这是正常的，如果您没有安装deepagents库，程序会自动降级到简化模式。

### API密钥错误

确保您已在环境变量或命令行参数中正确设置了Tavily API密钥。

## 许可证

MIT