import os
import json
import requests
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = os.getenv("DEEPSEEK_API_URL") or "https://api.deepseek.com"


def analyze_content(title: str, content: str) -> dict:
    prompt = f"""请分析以下网页内容，提取关键信息。

标题: {title}

内容:
{content[:4000]}

请以JSON格式返回分析结果，包含以下字段:
- summary: 一段简洁的总结（50字以内）
- main_content: 文章的主要/核心内容（100字以内）
- key_points: 3-5个关键要点（数组，每项不超过50字）
- notes: 3-5个需要注意的要点（数组，比如局限性、前提条件、适用范围等，每项不超过50字）
- value: 这篇文章的收藏价值，为什么值得收藏（50字以内）
- tags: 3-5个标签（数组，每项不超过10字，用于知识分类）

只返回JSON，不要包含其他文字。"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}]
    }

    print(f"=== 开始调用 DeepSeek API ===")
    print(f"API URL: {API_URL}/chat/completions")
    print(f"Content length: {len(content)} chars")

    try:
        response = requests.post(f"{API_URL}/chat/completions", headers=headers, json=payload, timeout=90)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        result_text = response.json()["choices"][0]["message"]["content"].strip()
        print(f"LLM 返回: {result_text[:200]}...")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误: {e}")
        print(f"Response body: {response.text}")
        return {
            "summary": "暂无摘要",
            "main_content": "",
            "key_points": [],
            "notes": [],
            "value": "",
            "tags": []
        }
    except Exception as e:
        print(f"API调用失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "summary": "暂无摘要",
            "main_content": "",
            "key_points": [],
            "notes": [],
            "value": "",
            "tags": []
        }

    try:
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]

        result_text = result_text.strip()
        parsed = json.loads(result_text)

        summary_text = parsed.get("summary", "")
        if not summary_text or len(summary_text.strip()) < 5:
            summary_text = "暂无摘要"

        return {
            "summary": summary_text[:100],
            "main_content": str(parsed.get("main_content", ""))[:150],
            "key_points": [str(p)[:80] for p in parsed.get("key_points", [])[:5]] if parsed.get("key_points") else [],
            "notes": [str(n)[:80] for n in parsed.get("notes", [])[:5]] if parsed.get("notes") else [],
            "value": str(parsed.get("value", ""))[:100],
            "tags": [str(t)[:20] for t in parsed.get("tags", [])[:5]] if parsed.get("tags") else []
        }
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}, 原始内容: {result_text[:200]}")
        return {
            "summary": "暂无摘要",
            "main_content": "",
            "key_points": [],
            "notes": [],
            "value": "",
            "tags": []
        }


def answer_question(question: str, context: list) -> dict:
    context_text = "\n\n".join([
        f"来源: {item['title']}\nURL: {item['url']}\n总结: {item.get('summary', '')}"
        for item in context
    ])

    prompt = f"""基于以下知识库内容回答用户问题。如果知识库中没有相关信息，请说明"知识库中没有相关信息"。

知识库内容:
{context_text}

用户问题: {question}

请用知识库中的内容回答，如果知识库中没有相关信息，请明确说明。"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(f"{API_URL}/chat/completions", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API调用失败: {e}")
        answer = "抱歉，API调用失败"

    return {
        "answer": answer,
        "sources": [{"title": item["title"], "url": item["url"]} for item in context]
    }


def analyze_paper(title: str, content: str) -> dict:
    """专门针对学术论文/文献的分析"""
    prompt = f"""请分析以下学术论文/文献，提取详细信息。

标题: {title}

内容（前5000字）:
{content[:5000]}

请以JSON格式返回分析结果，包含以下字段:
- summary: 论文摘要（100字以内）
- main_content: 论文的核心研究内容和目标（100字以内）
- key_points: 3-5个关键要点（如方法、贡献、发现等，每项不超过50字）
- notes: 3-5个需要注意的要点（如局限性、前提条件、适用范围、实验方法等，每项不超过50字）
- value: 这篇论文的学术价值和应用场景（50字以内）
- tags: 5-8个标签（学术领域、研究方法、技术关键词等，每项不超过10字）
- entities: 提取的关键实体，包含:
  - authors: 作者列表
  - methods: 使用的方法/技术
  - datasets: 使用的数据集
  - applications: 应用领域

只返回JSON，不要包含其他文字。"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    }

    print(f"=== 开始论文分析 DeepSeek API ===")
    print(f"Content length: {len(content)} chars")

    try:
        response = requests.post(f"{API_URL}/chat/completions", headers=headers, json=payload, timeout=120)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        result_text = response.json()["choices"][0]["message"]["content"].strip()
        print(f"LLM 返回: {result_text[:200]}...")
    except Exception as e:
        print(f"API调用失败: {e}")
        return {
            "summary": "暂无摘要",
            "main_content": "",
            "key_points": [],
            "notes": [],
            "value": "",
            "tags": [],
            "entities": {}
        }

    try:
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]

        result_text = result_text.strip()
        parsed = json.loads(result_text)

        summary_text = parsed.get("summary", "")
        if not summary_text or len(summary_text.strip()) < 5:
            summary_text = "暂无摘要"

        return {
            "summary": summary_text[:150],
            "main_content": str(parsed.get("main_content", ""))[:150],
            "key_points": [str(p)[:80] for p in parsed.get("key_points", [])[:5]] if parsed.get("key_points") else [],
            "notes": [str(n)[:80] for n in parsed.get("notes", [])[:5]] if parsed.get("notes") else [],
            "value": str(parsed.get("value", ""))[:100],
            "tags": [str(t)[:20] for t in parsed.get("tags", [])[:8]] if parsed.get("tags") else [],
            "entities": parsed.get("entities", {})
        }
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return {
            "summary": "暂无摘要",
            "main_content": "",
            "key_points": [],
            "notes": [],
            "value": "",
            "tags": [],
            "entities": {}
        }
