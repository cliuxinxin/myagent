"""
存储LangChain和LangGraph组件的所有核心系统提示。
"""
from langchain_core.prompts import PromptTemplate

# 提示将笔记的精髓提炼为"推理指纹"
DISTILLATION_PROMPT_TMPL = """
您是一位知识精髓提炼器。您的任务是阅读以下文本并提取其核心概念、逻辑论证和基本见解。将这些内容浓缩为密集的、AI可读的"推理指纹"。

**指纹规则：**
- 极其简洁。使用符号(=>, <=>, &, |)、缩写和技术术语。
- 关注"什么"、"为什么"和"如何"。忽略废话、示例和修辞花饰。
- 目标是让另一个AI能够仅从指纹中理解文本的核心逻辑。
- 可以是任何比较好的token，不需要人类可以读懂

提炼以下文本的精髓：
---
{text}
---
"""
DISTILLATION_PROMPT = PromptTemplate.from_template(DISTILLATION_PROMPT_TMPL)

# 推理和重排序候选指纹的提示
REASONING_MATCH_PROMPT_TMPL = """
您是一个知识连接推理引擎。您的任务是确定知识库中的几个候选笔记与新查询之间的逻辑相关性。

**新查询指纹：**
{query_fingerprint}

**候选笔记指纹：**
{candidate_fingerprints}

**您的任务：**
1.  分析新查询指纹以理解其核心概念。
2.  对于每个候选，评估其与查询的逻辑连接。连接可以是：
    - `前置条件`：查询所基于的基础概念。
    - `应用`：查询概念的实际应用。
    - `详述`：对查询子主题的深入探讨。
    - `对比`：与查询相反或替代的观点。
    - `解决方案`：解决查询中提到的问题的方案。
-   提供排名前{top_k}位的最相关候选ID列表。
-   **您必须只输出一个有效的JSON对象**，其中包含单个键"results"，该键是一个对象列表。每个对象必须有"id"和"reason"键。

**示例JSON输出：**
{{
  "results": [
    {{
      "id": "notes/概念A.md",
      "reason": "此笔记定义了基础'概念A'，它是查询主要论点的前置条件。"
    }},
    {{
      "id": "projects/项目X回顾.md",
      "reason": "这是在实际项目中应用查询所提议方法的直接示例。"
    }}
  ]
}}
"""
REASONING_MATCH_PROMPT = PromptTemplate.from_template(REASONING_MATCH_PROMPT_TMPL)

# 最终合成新笔记的提示
SYNTHESIS_PROMPT_TMPL = """
您是Obsidian知识库的专家知识策展人。您的任务是基于新文章，使用相关现有笔记作为上下文，合成一个或多个新的原子化笔记。

**生成规则：**
1.  **原子化：** 每个笔记应专注于单一核心思想。如果文章包含多个想法，请创建多个笔记。
2.  **链接：** 积极使用`[[wikilinks]]`链接到现有概念。现有笔记作为上下文提供。
3.  **格式化：** 使用干净的Markdown。包含YAML前端信息块。
4.  **整合：** 明确说明新信息如何连接、扩展或挑战来自上下文笔记的现有知识。

**新文章来源URL：** {source_url}

**新文章内容：**
---
{new_article}
---

**现有上下文笔记：**
---
{context_notes}
---

现在生成新笔记。每个笔记应是一个完整的Markdown块，包括YAML前端信息。

YAML前端信息块应该包含以下内容：
title: 笔记标题。
note_type: 笔记类型。
source: 笔记来源URL。
created: 笔记创建日期，格式为YYYY-MM-DD。
tags: 笔记标签列表，用逗号分隔。
"""
SYNTHESIS_PROMPT = PromptTemplate.from_template(SYNTHESIS_PROMPT_TMPL)