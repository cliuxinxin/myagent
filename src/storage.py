"""
管理用于存储和检索知识指纹的SQLite数据库。
此模块与框架无关。
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi


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
            使用 BM25 对 fingerprint_text 进行检索与排序。
            """
            # 取全部文档
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reasoning_index")
                rows = cursor.fetchall()

            if not rows:
                return []

            # 仅使用 fingerprint_text 构建语料
            corpus_texts = [
                (row["fingerprint_text"] or "")
                for row in rows
            ]

            # 简单分词，可按需替换为 jieba.lcut
            tokenized_corpus = [text.split() for text in corpus_texts]

            # 初始化 BM25
            bm25 = BM25Okapi(tokenized_corpus)

            # 查询处理
            tokenized_query = query.split()

            # 得分计算
            scores = bm25.get_scores(tokenized_query)

            # 取 top_k 索引
            ranked_indices = sorted(
                range(len(scores)),
                key=lambda i: scores[i],
                reverse=True
            )[:top_k]

            # 组装结果
            results = [dict(rows[i]) for i in ranked_indices]
            return results