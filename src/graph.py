"""
核心LangGraph定义和节点。
定义了处理新文章的有状态图。
"""
import json
import os
from typing import List, Dict, Any
from typing_extensions import TypedDict
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from pydantic import SecretStr

import config
from src import storage
from src.prompts import DISTILLATION_PROMPT, REASONING_MATCH_PROMPT, SYNTHESIS_PROMPT


# 定义图的状态
class KnowledgeAlchemistState(TypedDict):
    article_text: str
    source_url: str
    query_fingerprint: str
    candidates: List[Dict[str, Any]]
    ranked_candidates: List[Dict[str, Any]]
    context_notes: List[Dict[str, Any]]
    final_note: str


# 定义图的节点
def distill_fingerprint_node(state: KnowledgeAlchemistState) -> Dict[str, Any]:
    """提炼新文章的指纹。"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    llm_instance = ChatDeepSeek(
        model=config.ALCHEMY_LLM_MODEL,
        api_key=SecretStr(api_key) if api_key else None
    )
    prompt = DISTILLATION_PROMPT.format(text=state["article_text"])
    response = llm_instance.invoke(prompt)
    fingerprint = response.content if hasattr(response, 'content') else str(response)
    # 确保指纹是字符串
    if not isinstance(fingerprint, str):
        fingerprint = str(fingerprint)
    return {"query_fingerprint": fingerprint}


def filter_candidates_node(state: KnowledgeAlchemistState) -> Dict[str, Any]:
    """使用BM25过滤候选笔记。"""
    store_instance = storage.ReasoningIndexStore()
    candidates = store_instance.search_by_bm25(
        query=state["query_fingerprint"],
        top_k=config.LIBRARIAN_TOP_K
    )
    return {"candidates": candidates}


def reason_and_rerank_node(state: KnowledgeAlchemistState) -> Dict[str, Any]:
    """使用LLM推理和重排序候选笔记。"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    llm_instance = ChatDeepSeek(
        model=config.ALCHEMY_LLM_MODEL,
        api_key=SecretStr(api_key) if api_key else None
    )
    
    # 格式化候选指纹
    candidate_fingerprints = "\n".join([
        f"ID: {c['doc_id']}\n指纹: {c['fingerprint_text']}"
        for c in state["candidates"]
    ])
    
    # 构建推理提示
    prompt = REASONING_MATCH_PROMPT.format(
        query_fingerprint=state["query_fingerprint"],
        candidate_fingerprints=candidate_fingerprints,
        top_k=config.FINAL_TOP_K
    )
    
    # 获取LLM响应
    response = llm_instance.invoke(prompt)
    result_text = response.content if hasattr(response, 'content') else str(response)
    # 确保结果是字符串
    if not isinstance(result_text, str):
        result_text = str(result_text)
    
    # 解析响应
    try:
        result = json.loads(result_text)
        ranked_ids = [item["id"] for item in result["results"]]
        
        # 根据排名ID排序候选
        ranked_candidates = []
        for ranked_id in ranked_ids:
            for candidate in state["candidates"]:
                if candidate["doc_id"] == ranked_id:
                    ranked_candidates.append(candidate)
                    break
        
        return {"ranked_candidates": ranked_candidates[:config.FINAL_TOP_K]}
    except (json.JSONDecodeError, KeyError):
        # 如果解析失败，使用前N个候选
        return {"ranked_candidates": state["candidates"][:config.FINAL_TOP_K]}


def fetch_context_node(state: KnowledgeAlchemistState) -> Dict[str, Any]:
    """获取上下文笔记的完整文本。"""
    store_instance = storage.ReasoningIndexStore()
    context_notes = []
    for candidate in state["ranked_candidates"]:
        doc = store_instance.get_document(candidate["doc_id"])
        if doc:
            context_notes.append(doc)
    
    return {"context_notes": context_notes}


def synthesize_note_node(state: KnowledgeAlchemistState) -> Dict[str, Any]:
    """合成最终的新笔记。"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    llm_instance = ChatDeepSeek(
        model=config.ALCHEMY_LLM_MODEL,
        api_key=SecretStr(api_key) if api_key else None
    )
    
    # 格式化上下文笔记
    context_notes_text = "\n---\n".join([
        f"笔记ID: {note['doc_id']}\n内容:\n{note['full_text']}"
        for note in state["context_notes"]
    ])
    
    # 构建合成提示
    prompt = SYNTHESIS_PROMPT.format(
        source_url=state["source_url"],
        new_article=state["article_text"],
        context_notes=context_notes_text
    )
    
    # 生成最终笔记
    response = llm_instance.invoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)
    # 确保响应是字符串
    if not isinstance(response_text, str):
        response_text = str(response_text)

    # 尝试解析JSON响应
    try:
        # 清理响应文本，移除可能的markdown代码块标记
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        parsed_response = json.loads(cleaned_text)
        final_note = parsed_response.get("knowledge_points", [])
    except (json.JSONDecodeError, Exception) as e:
        print(f"解析JSON响应时出错: {e}")
        # 如果解析失败，返回原始文本作为单个知识点
        final_note = [{
            "title": "生成的笔记",
            "content": response_text
        }]

    return {"final_note": final_note}


# 构建图
def create_knowledge_alchemist_graph():
    """创建知识炼金术师图。"""
    graph = StateGraph(KnowledgeAlchemistState)
    
    # 添加节点
    graph.add_node("distill_fingerprint", distill_fingerprint_node)
    graph.add_node("filter_candidates", filter_candidates_node)
    graph.add_node("reason_and_rerank", reason_and_rerank_node)
    graph.add_node("fetch_context", fetch_context_node)
    graph.add_node("synthesize_note", synthesize_note_node)
    
    # 添加边
    graph.add_edge("distill_fingerprint", "filter_candidates")
    graph.add_edge("filter_candidates", "reason_and_rerank")
    graph.add_edge("reason_and_rerank", "fetch_context")
    graph.add_edge("fetch_context", "synthesize_note")
    graph.add_edge("synthesize_note", END)
    
    # 设置入口点
    graph.set_entry_point("distill_fingerprint")
    
    return graph.compile()


# 创建图实例
knowledge_alchemist_graph = create_knowledge_alchemist_graph()


def process_article(article_text: str, source_url: str = "") -> str:
    """处理新文章的便捷函数。"""
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    initial_state: KnowledgeAlchemistState = {
        "article_text": article_text,
        "source_url": source_url,
        "query_fingerprint": "",
        "candidates": [],
        "ranked_candidates": [],
        "context_notes": [],
        "final_note": ""
    }
    
    # 运行图
    final_state = knowledge_alchemist_graph.invoke(initial_state)
    
    return final_state["final_note"]