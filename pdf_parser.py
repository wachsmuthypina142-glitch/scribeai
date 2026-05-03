import os
import re
from typing import Optional, Dict, Any
from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    """从 PDF 文件提取文本"""
    try:
        reader = PdfReader(pdf_path)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = "\n".join(text_parts)
        return full_text
    except Exception as e:
        print(f"PDF 解析错误: {e}")
        return ""


def extract_pdf_metadata(pdf_path: str) -> Dict[str, Any]:
    """提取 PDF 元数据"""
    try:
        reader = PdfReader(pdf_path)
        metadata = reader.metadata or {}

        return {
            "title": metadata.get("/Title", ""),
            "author": metadata.get("/Author", ""),
            "subject": metadata.get("/Subject", ""),
            "creator": metadata.get("/Creator", ""),
            "producer": metadata.get("/Producer", ""),
            "page_count": len(reader.pages)
        }
    except Exception as e:
        print(f"元数据提取错误: {e}")
        return {"page_count": 0}


def extract_first_pages_text(pdf_path: str, max_pages: int = 5) -> str:
    """提取 PDF 前几页文本（用于快速分析）"""
    try:
        reader = PdfReader(pdf_path)
        text_parts = []

        num_pages = min(max_pages, len(reader.pages))
        for i in range(num_pages):
            page_text = reader.pages[i].extract_text()
            if page_text:
                text_parts.append(page_text)

        return "\n".join(text_parts)
    except Exception as e:
        print(f"PDF 前几页提取错误: {e}")
        return ""


def parse_pdf(file_path: str) -> Dict[str, Any]:
    """解析 PDF 文件，返回完整信息"""
    if not os.path.exists(file_path):
        return {"success": False, "error": "文件不存在"}

    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext != ".pdf":
        return {"success": False, "error": "不是 PDF 文件"}

    metadata = extract_pdf_metadata(file_path)
    full_text = extract_text_from_pdf(file_path)
    preview_text = extract_first_pages_text(file_path, max_pages=3)

    title = metadata.get("title") or os.path.basename(file_path)
    if title.endswith(".pdf"):
        title = title[:-4]

    return {
        "success": True,
        "title": title,
        "author": metadata.get("author", ""),
        "page_count": metadata.get("page_count", 0),
        "content": full_text[:15000],
        "preview": preview_text,
        "metadata": metadata
    }
