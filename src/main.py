"""
FastAPI服务器，通过API暴露LangGraph逻辑。
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union

from src.graph import process_article

# 创建FastAPI应用
app = FastAPI(
    title="知识炼金术师 API",
    description="一个使用LangGraph和DeepSeek API的AI系统，用于处理文章并生成与现有知识库关联的新笔记。",
    version="0.1.0"
)


# 定义知识点模型
class KnowledgePoint(BaseModel):
    title: str
    content: str


# 定义请求和响应模型
class ArticleRequest(BaseModel):
    text: str
    source_url: Optional[str] = ""


class ArticleResponse(BaseModel):
    generated_note: Union[List[KnowledgePoint], str]  # 支持新格式（列表）和旧格式（字符串）


# API端点
@app.post("/process-article", response_model=ArticleResponse)
async def process_article_endpoint(request: ArticleRequest):
    """
    处理新文章并生成关联的笔记。
    
    - **text**: 新文章的内容
    - **source_url**: 文章的来源URL（可选）
    """
    generated_note = process_article(request.text, request.source_url)
    return ArticleResponse(generated_note=generated_note)


@app.get("/")
async def root():
    """根端点，提供API信息。"""
    return {
        "message": "知识炼金术师 API",
        "description": "使用LangGraph和DeepSeek API处理文章并生成关联笔记。",
        "endpoints": {
            "process_article": "POST /process-article - 处理新文章并生成关联笔记"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查端点。"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)