import requests
from bs4 import BeautifulSoup
from typing import Optional
import time
import random


def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)


def fetch_url_content(url: str, max_retries: int = 3) -> dict:
    print(f"=== 开始抓取网页: {url} ===")

    headers_list = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        },
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        },
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    ]

    special_sites = {
        "zhihu.com": "知乎需要登录才能访问完整内容，建议使用浏览器插件直接收藏",
        "weixin.qq.com": "微信公众号需要特殊处理，建议直接复制内容收藏",
        "jianshu.com": "简书",
    }

    for site, tip in special_sites.items():
        if site in url.lower():
            print(f"提示: {tip}")
            return {
                "success": False,
                "error": f"网站限制: {tip}",
                "tip": tip
            }

    last_error = None
    for attempt in range(max_retries):
        headers = random.choice(headers_list).copy()

        try:
            time.sleep(random.uniform(0.5, 2.0))

            response = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
            print(f"抓取响应状态: {response.status_code} (尝试 {attempt + 1}/{max_retries})")

            if response.status_code == 403:
                last_error = f"403 访问被拒绝 (尝试 {attempt + 1}/{max_retries})"
                continue

            if response.status_code == 429:
                last_error = "429 请求过于频繁，请稍后再试"
                time.sleep(5)
                continue

            response.raise_for_status()

            try:
                response.encoding = response.apparent_encoding or 'utf-8'
            except:
                response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, "lxml")

            title = None
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"].strip()

            if not title:
                title_tag = soup.find("title")
                if title_tag:
                    title = title_tag.get_text(strip=True)

            if not title:
                h1_tag = soup.find("h1")
                if h1_tag:
                    title = h1_tag.get_text(strip=True)

            if not title:
                title = url

            content = extract_text_from_html(response.text)

            if len(content) < 100:
                last_error = "网页内容过少，可能需要登录或内容被限制"
                continue

            content = content[:8000]

            print(f"抓取成功，内容长度: {len(content)} 字符")
            return {
                "success": True,
                "url": url,
                "title": title,
                "content": content
            }

        except requests.RequestException as e:
            last_error = str(e)
            print(f"抓取失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2 + random.uniform(0, 1)
                print(f"等待 {wait_time:.1f} 秒后重试...")
                time.sleep(wait_time)

    print(f"抓取最终失败: {last_error}")
    return {
        "success": False,
        "error": f"抓取失败: {last_error}"
    }
