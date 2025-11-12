"""
管理用于存储和检索知识指纹的SQLite数据库。
此模块与框架无关。
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import config


class ReasoningIndexStore:
    """管理用于存储和检索文档的SQLite数据库。"""

    def __init__(self, db_path: Path = config.DB_PATH):
        self.db_path = db_path
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reasoning_index (
                    doc_id TEXT PRIMARY KEY,
                    metadata TEXT,
                    fingerprint_text TEXT,
                    full_text TEXT
                )
            """)
            conn.commit()

    def add_or_update_document(
        self, doc_id: str, metadata: Dict[str, Any],
        fingerprint_text: str, full_text: str
    ):
        """在索引中添加或更新文档。"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO reasoning_index
                (doc_id, metadata, fingerprint_text, full_text)
                VALUES (?, ?, ?, ?)
                """,
                (doc_id, json.dumps(metadata), fingerprint_text, full_text)
            )
            conn.commit()

    def delete_document(self, doc_id: str):
        """从索引中删除文档。"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reasoning_index WHERE doc_id = ?", (doc_id,))
            conn.commit()

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """通过ID检索单个文档。"""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reasoning_index WHERE doc_id = ?", (doc_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """从索引中检索所有文档。"""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reasoning_index")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def search_by_bm25(self, query: str, top_k: int = config.LIBRARIAN_TOP_K) -> List[Dict[str, Any]]:
        """
        使用BM25搜索指纹文本。
        注意：这是一个简化的实现。在生产环境中，您可能想要使用专门的搜索引擎如Elasticsearch。
        """
        # 这里我们使用简单的LIKE查询来模拟BM25搜索
        # 在实际实现中，您应该使用rank_bm25库或其他搜索引擎
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            search_query = f"%{query}%"
            cursor.execute("""
                SELECT * FROM reasoning_index 
                WHERE fingerprint_text LIKE ? OR full_text LIKE ?
                ORDER BY LENGTH(fingerprint_text) 
                LIMIT ?
            """, (search_query, search_query, top_k))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]