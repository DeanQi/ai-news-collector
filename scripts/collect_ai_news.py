#!/usr/bin/env python3
"""AI日报采集脚本 - 精简版，采集 ArXiv + GitHub Trending 推送飞书"""

import os
import sys
import json
import requests
import feedparser
from datetime import datetime, timezone

# --- 配置 ---
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK_URL", "")
BEIJING_TZ_OFFSET = timezone.utc

# --- ArXiv 采集 ---
ARXIV_NAMES = {
    "Kaiming He": "Kaiming_He",
    "Yann LeCun": "Yann_LeCun",
    "Geoffrey Hinton": "Geoffrey_Hinton",
    "Andrew Ng": "Andrew_Ng",
    "Fei-Fei Li": "Fei-Fei_Li",
    "Yoshua Bengio": "Yoshua_Bengio",
    "Demis Hassabis": "Demis_Hassabis",
    "Ilya Sutskever": "Ilya_Sutskever",
    "Zico Kolter": "Zico_Kolter",
    "Pieter Abbeel": "Pieter_Abbeel",
}

def fetch_arxiv_papers(arxiv_name, max_results=3):
    query = arxiv_name.lower().replace(" ", "_")
    url = f"http://export.arxiv.org/api/query?search_query=au:{query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        papers = []
        for entry in feed.entries[:max_results]:
            title = entry.get("title", "Unknown").strip().replace("\n", " ")
            title = " ".join(title.split())
            arxiv_id = entry.get("id", "").split("/abs/")[-1]
            arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
            published_str = entry.get("published", "")
            try:
                published = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
                date_str = published.strftime("%Y-%m-%d")
            except Exception:
                date_str = published_str[:10] if published_str else "Unknown"
            summary = entry.get("summary", "")[:200].strip()
            papers.append({"title": title, "url": arxiv_url, "date": date_str, "summary": summary})
        return papers
    except Exception as e:
        print(f"[ArXiv] {arxiv_name}: {e}")
        return []

# --- GitHub Trending ---
def fetch_github_trending():
    try:
        url = "https://api.github.com/search/repositories?q=created:>2024-01-01&sort=stars&order=desc&per_page=5"
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "AI-News-Collector"}
        resp = requests.get(url, headers=headers, timeout=20)
        data = resp.json()
        repos = []
        for item in data.get("items", [])[:5]:
            repos.append({
                "name": item.get("full_name", ""),
                "url": item.get("html_url", ""),
                "desc": (item.get("description", "") or "")[:100],
                "stars": item.get("stargazers_count", 0),
            })
        return repos
    except Exception as e:
        print(f"[GitHub]: {e}")
        return []

# --- 飞书推送 ---
def send_to_feishu(title, sections):
    if not FEISHU_WEBHOOK:
        print("No FEISHU_WEBHOOK_URL set, skipping push")
        return False

    blocks = [{"tag": "text", "text": title + "\n"}]
    for sec_title, items in sections:
        blocks.append({"tag": "text", "text": f"\n【{sec_title}】\n"})
        for item in items:
            if "stars" in item:
                blocks.append({"tag": "text", "text": f"{item['name']}  [{item['stars']}]({item['url']})\n  {item.get('desc', '')}\n"})
            elif "summary" in item:
                blocks.append({"tag": "text", "text": f"**[{item['title']}]({item['url']})**\n  {item.get('summary', '')[:100]}\n"})
            else:
                blocks.append({"tag": "text", "text": f"**[{item['title']}]({item['url']})**\n"})

    payload = {
        "msg_type": "post",
        "content": {"post": {"zh_cn": {"title": title, "content": blocks}}}
    }

    try:
        r = requests.post(FEISHU_WEBHOOK, json=payload, timeout=15)
        result = r.json()
        print(f"[Feishu] Response: {result}")
        return result.get("code") == 0
    except Exception as e:
        print(f"[Feishu] Error: {e}")
        return False

# --- 主流程 ---
def main():
    print("=== AI Daily News Collector ===\n")

    # ArXiv
    print("Fetching ArXiv...")
    arxiv_items = []
    for name, _ in list(ARXIV_NAMES.items())[:5]:  # Limit to 5 for speed
        papers = fetch_arxiv_papers(name, max_results=1)
        if papers:
            arxiv_items.append({"title": f"{name}: {papers[0]['title']}", "url": papers[0]["url"], "date": papers[0]["date"], "summary": papers[0]["summary"]})

    # GitHub
    print("Fetching GitHub trending...")
    github_items = fetch_github_trending()

    # Push
    print("Pushing to Feishu...")
    sections = [("ArXiv 最新论文", arxiv_items), ("GitHub Trending", github_items)]
    success = send_to_feishu("AI 日报", sections)

    if success:
        print("\nFeishu push SUCCESS!")
    else:
        print("\nFeishu push FAILED or skipped")

if __name__ == "__main__":
    main()
