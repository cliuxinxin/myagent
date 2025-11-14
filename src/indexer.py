"""
知识索引器和文件监视器。
负责扫描Vault以构建初始推理索引，并监视文件更改以保持索引最新。
"""
import os
import time
import hashlib
import json
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


def needs_processing(file_path: Path) -> bool:
    """检查文件是否需要重新处理。"""
    try:
        # 确保使用正确的路径
        vault_path = Path(config.VAULT_PATH)
        if not file_path.is_absolute():
            # 如果是相对路径，转换为相对于vault的绝对路径
            file_path = vault_path / file_path

        doc_id = str(file_path.relative_to(vault_path))
        existing_doc = store.get_document(doc_id)

        # 如果文件不在数据库中，需要处理
        if existing_doc is None:
            return True

        # 检查文件修改时间
        current_metadata = extract_metadata(file_path)
        stored_metadata = json.loads(existing_doc['metadata'])

        # 如果文件修改时间更新，需要处理
        if current_metadata['modified_time'] > stored_metadata['modified_time']:
            return True

        # 如果文件大小改变，需要处理
        if current_metadata['file_size'] != stored_metadata['file_size']:
            return True

        return False
    except Exception as e:
        print(f"检查文件 {file_path} 是否需要处理时出错: {e}")
        return True  # 出错时默认处理


def process_note_file(file_path: Path):
    """处理单个笔记文件，生成指纹并存储。"""
    try:
        # 检查是否需要处理
        if not needs_processing(file_path):
            doc_id = str(file_path.relative_to(config.VAULT_PATH))
            print(f"跳过未修改的文件: {doc_id}")
            return

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
    md_files = list(vault_path.rglob("*.md"))
    total_files = len(md_files)

    if total_files == 0:
        print("未找到.md文件")
        return

    print(f"找到 {total_files} 个.md文件")

    processed_count = 0
    skipped_count = 0

    for file_path in md_files:
        # 检查是否需要处理
        if not needs_processing(file_path):
            skipped_count += 1
            continue

        process_note_file(file_path)
        processed_count += 1

        # 显示进度
        if (processed_count + skipped_count) % 10 == 0:
            progress = (processed_count + skipped_count) / total_files * 100
            print(f"进度: {progress:.1f}% ({processed_count + skipped_count}/{total_files})")

    print(f"初始索引构建完成。")
    print(f"总文件数: {total_files}, 新处理: {processed_count}, 跳过: {skipped_count}")


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