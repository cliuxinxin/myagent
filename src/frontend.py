"""
知识炼金术师 - Streamlit前端界面
提供用户友好的Web界面来处理文章并生成关联笔记
"""
import streamlit as st
import requests
import json
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="知识炼金术师",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API配置
API_BASE_URL = "http://127.0.0.1:8000"

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """检查API服务器是否正常运行"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def process_article(text, source_url=""):
    """调用API处理文章"""
    try:
        payload = {
            "text": text,
            "source_url": source_url
        }

        with st.spinner("🧪 正在处理文章，请稍候..."):
            response = requests.post(
                f"{API_BASE_URL}/process-article",
                json=payload,
                timeout=600  # 10分钟超时
            )

        if response.status_code == 200:
            result = response.json()
            return result.get("generated_note", ""), None
        else:
            return None, f"API错误: {response.status_code} - {response.text}"

    except requests.exceptions.Timeout:
        return None, "请求超时，请稍后重试"
    except requests.exceptions.ConnectionError:
        return None, "无法连接到API服务器，请确保服务正在运行"
    except Exception as e:
        return None, f"处理文章时出错: {str(e)}"

def main():
    # 页面标题
    st.markdown('<div class="main-header">🧪 知识炼金术师</div>', unsafe_allow_html=True)

    # 侧边栏 - 系统信息
    with st.sidebar:
        st.header("系统状态")

        # 检查API健康状态
        if check_api_health():
            st.success("✅ API服务器运行正常")
        else:
            st.error("❌ API服务器未运行")
            st.info("请确保已启动API服务器：\n```bash\n./start.sh\n```")

        st.markdown("---")
        st.header("使用说明")
        st.markdown("""
        1. 在下方输入文章内容
        2. 可选：填写来源URL
        3. 点击"处理文章"按钮
        4. 系统将生成关联的笔记
        """)

        st.markdown("---")
        st.header("关于")
        st.markdown("""
        知识炼金术师是一个AI系统，能够：

        - 📚 分析新文章内容
        - 🔗 关联现有知识库
        - 🧠 生成原子化笔记
        - 📝 遵循Obsidian格式
        """)

    # 主内容区域
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📝 输入文章")

        # 文章输入
        article_text = st.text_area(
            "文章内容",
            height=300,
            placeholder="请输入要处理的文章内容...",
            help="输入您想要分析和关联到知识库的文章内容"
        )

        # 来源URL
        source_url = st.text_input(
            "来源URL (可选)",
            placeholder="https://example.com/article",
            help="文章的来源链接，用于引用"
        )

        # 处理按钮
        if st.button("🧪 处理文章", type="primary", use_container_width=True):
            if not article_text.strip():
                st.error("请输入文章内容")
            else:
                if not check_api_health():
                    st.error("API服务器未运行，请先启动服务")
                else:
                    result, error = process_article(article_text, source_url)

                    if error:
                        st.markdown(f'<div class="error-box">{error}</div>', unsafe_allow_html=True)
                    else:
                        st.session_state.generated_note = result
                        st.session_state.processed_at = datetime.now()
                        st.success("✅ 文章处理完成！")

    with col2:
        st.header("📖 生成的笔记")

        if "generated_note" in st.session_state:
            # 显示处理时间
            if "processed_at" in st.session_state:
                st.caption(f"处理时间: {st.session_state.processed_at.strftime('%Y-%m-%d %H:%M:%S')}")

            # 显示生成的笔记
            st.markdown(st.session_state.generated_note)

            # 操作按钮
            col_copy, col_download = st.columns(2)

            with col_copy:
                if st.button("📋 复制到剪贴板", use_container_width=True):
                    st.code(st.session_state.generated_note, language="markdown")
                    st.success("已复制到剪贴板")

            with col_download:
                # 创建下载链接
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_note_{timestamp}.md"
                st.download_button(
                    label="💾 下载笔记",
                    data=st.session_state.generated_note,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True
                )
        else:
            st.info("👆 请在左侧输入文章内容并点击'处理文章'按钮")

    # 示例部分
    st.markdown("---")
    st.header("💡 使用示例")

    example_col1, example_col2 = st.columns(2)

    with example_col1:
        st.subheader("示例文章")
        example_article = """机器学习是人工智能的一个重要分支，它使计算机能够从数据中学习并做出预测或决策，而无需进行明确的编程。深度学习作为机器学习的一个子领域，使用神经网络模拟人脑的工作方式，在图像识别、自然语言处理等领域取得了突破性进展。

近年来，随着计算能力的提升和大数据的普及，机器学习技术得到了快速发展。监督学习、无监督学习和强化学习是三种主要的机器学习方法。其中，监督学习需要标注数据来训练模型，而无监督学习则从无标签数据中发现模式。

在实际应用中，机器学习已经被广泛应用于推荐系统、自动驾驶、医疗诊断等多个领域，极大地改变了我们的生活方式和工作方式。"""

        if st.button("📋 加载示例文章", key="load_example"):
            st.session_state.article_text = example_article
            st.rerun()

    with example_col2:
        st.subheader("预期结果")
        st.markdown("""
        系统将：

        - 🔍 分析文章的核心概念
        - 📚 检索相关的现有笔记
        - 🧩 生成原子化的新笔记
        - 🔗 创建与现有知识的连接
        - 📝 输出Obsidian格式的笔记
        """)

if __name__ == "__main__":
    main()