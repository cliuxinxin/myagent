"""
知识炼金术师项目的中心配置文件。
"""
import os
from pathlib import Path

# --- 核心路径 ---
# 重要：将此更改为您的Obsidian Vault的绝对路径
VAULT_PATH = "/Users/liuxinxin/Documents/GitHub/myagent/lang_vault/lang-vault"

# 项目根目录
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "reasoning_index.db"

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)

# --- 模型配置 ---
# 来自DeepSeek的强大"炼金术士"LLM，用于所有推理任务。
ALCHEMY_LLM_MODEL = "deepseek-chat"

# --- 检索器配置 ---
# 使用BM25获取候选之前要获取的候选数量
LIBRARIAN_TOP_K = 25
# LLM重排序后用作上下文的最终文档数量
FINAL_TOP_K = 5