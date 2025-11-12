# 知识炼金术师 (LangGraph版)

**知识炼金术师** 是一个原型AI系统，旨在与个人知识库（如Obsidian vault）深度集成。它使用新颖的"LLM作为检索器"方法，在新信息与现有知识之间创建有意义的连接，生成遵循原子化、链接化思维原则的新笔记。

本项目已重新架构，使用 **LangGraph** 进行AI流程的健壮且显式的状态管理，并使用 **DeepSeek** 作为核心语言模型。

## 🚀 快速启动

### 方法一：一键启动（推荐）

使用启动脚本一键启动所有服务：

```bash
# 一键启动所有服务
./start.sh

# 访问Streamlit前端
# 打开浏览器访问: http://localhost:8501
```

### 方法二：手动启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动索引器（终端1）
PYTHONPATH=/Users/liuxinxin/Documents/GitHub/myagent venv/bin/python src/indexer.py

# 3. 启动API服务器（终端2）
PYTHONPATH=/Users/liuxinxin/Documents/GitHub/myagent venv/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 4. 启动Streamlit前端（终端3）
PYTHONPATH=/Users/liuxinxin/Documents/GitHub/myagent venv/bin/streamlit run src/frontend.py

# 5. 访问前端界面
# 打开浏览器访问: http://localhost:8501
```

## 核心架构

系统的逻辑使用LangGraph定义为有状态图。在处理新文章时，系统会经历以下状态和操作：

1.  **提炼指纹：** 强大的"炼金术士"LLM (`deepseek-chat`) 阅读新文章并将其精髓提炼为密集的、AI可读的"推理指纹"。

2.  **筛选候选：** 在预构建的所有现有笔记指纹索引上执行快速的基于关键词的搜索(BM25)。这有效地选择出有希望进行深入分析的候选列表。

3.  **推理与重排序：** 炼金术士LLM执行**逻辑推理任务**。它将新文章的指纹与候选指纹进行比较，并返回最相关笔记的排序列表，同时提供为什么每个笔记相关的**理由**。

4.  **获取上下文：** 系统从知识库中检索排名靠前的笔记的完整文本。

5.  **合成笔记：** 炼金术士LLM使用原始文章和检索到的上下文笔记来合成一个新的、原子化的和互联的笔记，格式完全适合Obsidian vault。

## 项目结构

knowledge-alchemist-langgraph/
├── .env # 您的秘密API密钥
├── .env.example
├── config.py # 路径和模型的主要配置
├── requirements.txt
├── start.sh # 一键启动脚本
├── src/
│ ├── __init__.py
│ ├── storage.py # 管理推理索引的SQLite数据库
│ ├── prompts.py # 存储所有核心系统提示
│ ├── indexer.py # 构建和监视索引的逻辑
│ ├── graph.py # 核心LangGraph定义和节点
│ ├── main.py # 通过API暴露逻辑的FastAPI服务器
│ └── frontend.py # Streamlit前端界面
└── data/ # 存储SQLite数据库的目录
└── reasoning_index.db

## 设置说明

1.  **克隆仓库：**
    ```bash
    git clone <your_repo_url>
    cd knowledge-alchemist-langgraph
    ```

2.  **创建虚拟环境：**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows上使用: venv\Scripts\activate
    ```

3.  **安装依赖：**
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置环境变量：**
    *   将`.env.example`复制到名为`.env`的新文件。
    *   打开`.env`并添加您的**DeepSeek API密钥**。
    ```bash
    cp .env.example .env
    # 编辑.env文件，添加DEEPSEEK_API_KEY=sk-...
    ```

5.  **配置vault路径：**
    *   打开`config.py`并将`VAULT_PATH`变量设置为您的Obsidian vault的绝对路径。
    *   默认路径已配置为：`/Users/liuxinxin/Documents/GitHub/myagent/lang_vault/lang-vault`

## 如何运行

该系统有两个必须在不同终端中运行的主要组件。

### 方法一：手动启动（推荐用于开发）

1.  **索引器与监视器 (首先运行)：**
    此脚本对您的vault执行完整扫描以构建初始推理索引。之后，它会监视文件更改以保持索引最新。

    **重要：** 由于Python模块导入问题，需要使用PYTHONPATH环境变量

    ```bash
    # 激活虚拟环境
    source venv/bin/activate

    # 设置PYTHONPATH并启动索引器
    PYTHONPATH=/Users/liuxinxin/Documents/GitHub/myagent python src/indexer.py
    ```
    让此进程在后台运行。

2.  **FastAPI服务器：**
    此服务器通过Web API暴露LangGraph应用程序。

    ```bash
    # 激活虚拟环境（如果还没激活）
    source venv/bin/activate

    # 设置PYTHONPATH并启动服务器
    PYTHONPATH=/Users/liuxinxin/Documents/GitHub/myagent uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    ```
    您现在可以通过`http://127.0.0.1:8000/docs`访问API文档。

### 方法二：使用虚拟环境Python（推荐）

1.  **索引器：**
    ```bash
    PYTHONPATH=/Users/liuxinxin/Documents/GitHub/myagent venv/bin/python src/indexer.py
    ```

2.  **FastAPI服务器：**
    ```bash
    PYTHONPATH=/Users/liuxinxin/Documents/GitHub/myagent venv/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    ```

### 验证启动状态

- **索引器**：检查data目录是否生成`reasoning_index.db`文件
- **服务器**：访问 http://127.0.0.1:8000/health 应该返回 `{"status": "healthy"}`
- **API文档**：访问 http://127.0.0.1:8000/docs 查看完整的API文档

## API使用

向`http://127.0.0.1:8000/process-article`发送`POST`请求，携带JSON体：

```json
{
  "text": "您的新文章内容在这里...",
  "source_url": "http://example.com/article"
}

API将从图的最终状态返回生成的Markdown笔记。

## 🔧 故障排除

### 常见问题

1. **ModuleNotFoundError: No module named 'config'**
   - 解决方案：使用 `PYTHONPATH=/Users/liuxinxin/Documents/GitHub/myagent` 环境变量

2. **端口8000已被占用**
   - 解决方案：更改端口 `--port 8001` 或杀死占用端口的进程

3. **DEEPSEEK_API_KEY未设置**
   - 解决方案：确保.env文件存在且包含有效的DeepSeek API密钥

4. **索引器无法找到vault文件**
   - 解决方案：检查config.py中的VAULT_PATH配置是否正确

### 验证系统状态

```bash
# 检查数据库是否创建
ls -la data/reasoning_index.db

# 检查API健康状态
curl http://127.0.0.1:8000/health

# 检查API文档
curl http://127.0.0.1:8000/

# 检查Streamlit前端
curl http://localhost:8501/healthz
```

### 服务访问地址

- **Streamlit前端**: http://localhost:8501
- **API服务器**: http://127.0.0.1:8000
- **API文档**: http://127.0.0.1:8000/docs

### 日志查看

- **索引器日志**：在索引器终端查看文件处理状态
- **服务器日志**：在服务器终端查看API请求和响应
- **错误日志**：检查终端输出的错误信息