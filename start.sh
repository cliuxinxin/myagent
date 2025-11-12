#!/bin/bash

# 知识炼金术师 - 一键启动脚本
# 启动索引器、FastAPI服务器和Streamlit前端

set -e

echo "🚀 启动知识炼金术师系统..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行设置步骤"
    exit 1
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 设置PYTHONPATH
export PYTHONPATH=/Users/liuxinxin/Documents/GitHub/myagent

# 检查依赖是否安装
echo "🔍 检查依赖..."
python -c "import streamlit, requests" 2>/dev/null || {
    echo "📥 安装依赖..."
    pip install -r requirements.txt
}

# 启动索引器（后台）
echo "📚 启动索引器..."
python src/indexer.py &
INDEXER_PID=$!

# 等待索引器初始化
sleep 3

# 启动FastAPI服务器（后台）
echo "🌐 启动API服务器..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# 等待API服务器启动
sleep 5

# 启动Streamlit前端
echo "🎨 启动Streamlit前端..."
echo ""
echo "========================================"
echo "系统启动完成！"
echo "- API服务器: http://127.0.0.1:8000"
echo "- API文档: http://127.0.0.1:8000/docs"
echo "- Streamlit前端: http://localhost:8501"
echo "========================================"
echo ""

# 启动Streamlit
streamlit run src/frontend.py

# 清理：当Streamlit退出时，停止其他服务
echo "🛑 停止服务..."
kill $INDEXER_PID 2>/dev/null || true
kill $API_PID 2>/dev/null || true
echo "✅ 所有服务已停止"