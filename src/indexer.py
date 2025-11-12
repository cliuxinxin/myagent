"""
知识索引器和文件监视器。
负责扫描Vault以构建初始推理索引，并监视文件更改以保持索引最新。
"""
import os
import time
import hashlib
from pathlib import Path
from typing import Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import PromptTemplate
from pydantic import SecretStr
from dotenv import load_dotenv

import config
from src import storage
from src.prompts import DISTILLATION_PROMPT

# 加载环境变量
load_dotenv()

# 初始化存储和LLM
store = storage.ReasoningIndexStore()
api_key = os.environ.get("DEEPSEEK_API_KEY")
llm = ChatDeepSeek(
    model=config.ALCHEMY_LLM_MODEL,
    api_key=SecretStr(api_key) if api_key else None
)


def get_file_hash(file_path: Path) -> str:
    """计算文件内容的哈希值。"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def extract_metadata(file_path: Path) -> Dict[str, Any]:
    """从文件中提取元数据。"""
    stat = file_path.stat()
    return {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "created_time": stat.st_ctime,
        "modified_time": stat.st_mtime,
        "file_size": stat.st_size,
    }


def process_note_file(file_path: Path):
    """处理单个笔记文件，生成指纹并存储。"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取元数据
        metadata = extract_metadata(file_path)
        
        # 生成指纹
        fingerprint_prompt = DISTILLATION_PROMPT.format(text=content)
        response = llm.invoke(fingerprint_prompt)
        fingerprint = response.content if hasattr(response, 'content') else str(response)
        
        # 确保指纹是字符串
        if not isinstance(fingerprint, str):
            fingerprint = str(fingerprint)
        
        # 存储到索引
        doc_id = str(file_path.relative_to(config.VAULT_PATH))
        store.add_or_update_document(
            doc_id=doc_id,
            metadata=metadata,
            fingerprint_text=fingerprint,
            full_text=content
        )
        
        print(f"已处理文件: {doc_id}")
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")


def build_initial_index():
    """构建初始索引。"""
    print("开始构建初始索引...")
    
    # 遍历Vault中的所有.md文件
    vault_path = Path(config.VAULT_PATH)
    for file_path in vault_path.rglob("*.md"):
        process_note_file(file_path)
    
    print("初始索引构建完成。")


class VaultChangeHandler(FileSystemEventHandler):
    """处理Vault文件更改的事件处理器。"""
    
    def on_modified(self, event):
        if not event.is_directory:
            src_path_str = str(event.src_path)
            if src_path_str.endswith('.md'):
                file_path = Path(src_path_str)
                print(f"检测到文件修改: {file_path}")
                process_note_file(file_path)
    
    def on_created(self, event):
        if not event.is_directory:
            src_path_str = str(event.src_path)
            if src_path_str.endswith('.md'):
                file_path = Path(src_path_str)
                print(f"检测到新文件: {file_path}")
                process_note_file(file_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            src_path_str = str(event.src_path)
            if src_path_str.endswith('.md'):
                file_path = Path(src_path_str)
                vault_path = Path(config.VAULT_PATH)
                doc_id = str(file_path.relative_to(vault_path))
                store.delete_document(doc_id)
                print(f"已删除索引中的文件: {doc_id}")


def start_watching():
    """开始监视Vault的变化。"""
    event_handler = VaultChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(config.VAULT_PATH), recursive=True)
    observer.start()
    
    print(f"开始监视目录: {config.VAULT_PATH}")
    print("按 Ctrl+C 停止监视。")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("监视已停止。")
    
    observer.join()


if __name__ == "__main__":
    # 构建初始索引
    build_initial_index()

    # 开始监视
    start_watching()