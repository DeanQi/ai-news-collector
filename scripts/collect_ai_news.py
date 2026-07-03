#!/usr/bin/env python3
"""
AI圈大佬动态日报采集脚本
- 采集 ArXiv 最新论文
- 采集 GitHub 公开动态
- 采集 Twitter 动态（需配置 TWITTER_BEARER_TOKEN）
- 采集微博动态（需配置 WEIBO_COOKIE）
- 推送到飞书机器人 Webhook
"""

import os
import sys
import json
import time
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from collections import defaultdict

import requests
import feedparser
import pytz

# ─── 配置 ───────────────────────────────────────────────

FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")
WEIBO_COOKIE = os.environ.get("WEIBO_COOKIE", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

BEIJING_TZ = pytz.timezone("Asia/Shanghai")
TODAY = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
YESTERDAY = (datetime.now(BEIJING_TZ) - timedelta(days=1))
WEEK_AGO = (datetime.now(BEIJING_TZ) - timedelta(days=7))

# 每个数据源最多展示条数
MAX_PER_SOURCE = 1

# ─── 大佬信息库 ─────────────────────────────────────────

# 格式: { "name": "中文名/常用名", "arxiv_name": "ArXiv作者名(Last, First)", "github_user": "GitHub用户名或org", "twitter_id": "Twitter用户ID数字", "weibo_uid": "微博UID" }
BIG_NAMES = [
    # === 顶级研究机构/企业领袖 ===
    {"name": "Yann LeCun",           "arxiv_name": "LeCun, Yann",            "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Geoffrey Hinton",      "arxiv_name": "Hinton, Geoffrey",       "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Yoshua Bengio",        "arxiv_name": "Bengio, Yoshua",         "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Ilya Sutskever",       "arxiv_name": "Sutskever, Ilya",        "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Sam Altman",           "arxiv_name": "",                       "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Demis Hassabis",       "arxiv_name": "Hassabis, Demis",        "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "李飞飞 (Fei-Fei Li)",   "arxiv_name": "Li, Fei-Fei",            "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "吴恩达 (Andrew Ng)",    "arxiv_name": "Ng, Andrew",             "github_user": "andrewng",           "twitter_id": "", "weibo_uid": ""},

    # === 大模型/LLM方向 ===
    {"name": "Andrej Karpathy",      "arxiv_name": "Karpathy, Andrej",       "github_user": "karpathy",           "twitter_id": "", "weibo_uid": ""},
    {"name": "Dario Amodei",         "arxiv_name": "Amodei, Dario",          "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Aidan Gomez",          "arxiv_name": "Gomez, Aidan",           "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Noam Shazeer",         "arxiv_name": "Shazeer, Noam",          "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "梁文锋 (DeepSeek)",     "arxiv_name": "",                       "github_user": "deepseek-ai",        "twitter_id": "", "weibo_uid": ""},

    # === 开源/工具生态 ===
    {"name": "Clement Delangue",     "arxiv_name": "",                       "github_user": "ClementDelangue",    "twitter_id": "", "weibo_uid": ""},
    {"name": "Thomas Wolf",          "arxiv_name": "",                       "github_user": "thomwolf",           "twitter_id": "", "weibo_uid": ""},
    {"name": "Lukas Biewald",        "arxiv_name": "",                       "github_user": "lukas",              "twitter_id": "", "weibo_uid": ""},

    # === 中国AI圈 ===
    {"name": "张亚勤",               "arxiv_name": "Zhang, Ya-Qin",           "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "唐杰 (智谱/ChatGLM)",   "arxiv_name": "Tang, Jie",              "github_user": "THUDM",              "twitter_id": "", "weibo_uid": ""},
    {"name": "王小川 (百川智能)",     "arxiv_name": "",                       "github_user": "baichuan-inc",       "twitter_id": "", "weibo_uid": ""},
    {"name": "李开复 (零一万物)",     "arxiv_name": "Lee, Kai-Fu",            "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "周鸿祎 (360)",         "arxiv_name": "",                       "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "黄仁勋 (Jensen Huang)", "arxiv_name": "",                       "github_user": "",                   "twitter_id": "", "weibo_uid": ""},

    # === 学术前沿 ===
    {"name": "Percy Liang",          "arxiv_name": "Liang, Percy",           "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Jim Fan",              "arxiv_name": "Fan, Jim",               "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Christopher Manning",  "arxiv_name": "Manning, Christopher",   "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Pieter Abbeel",        "arxiv_name": "Abbeel, Pieter",         "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Sergey Levine",        "arxiv_name": "Levine, Sergey",         "github_user": "",                   "twitter_id": "", "weibo_uid": ""},

    # === 重要组织/团队 ===
    {"name": "Meta FAIR",            "arxiv_name": "",                       "github_user": "facebookresearch",   "twitter_id": "", "weibo_uid": ""},
    {"name": "Google DeepMind",      "arxiv_name": "",                       "github_user": "google-deepmind",    "twitter_id": "", "weibo_uid": ""},
    {"name": "OpenAI",               "arxiv_name": "",                       "github_user": "openai",             "twitter_id": "", "weibo_uid": ""},
    {"name": "Anthropic",            "arxiv_name": "",                       "github_user": "anthropics",         "twitter_id": "", "weibo_uid": ""},
    {"name": "Cohere",               "arxiv_name": "",                       "github_user": "cohere-ai",          "twitter_id": "", "weibo_uid": ""},
    {"name": "HuggingFace",          "arxiv_name": "",                       "github_user": "huggingface",        "twitter_id": "", "weibo_uid": ""},
]


# ─── ArXiv 论文采集 ────────────────────────────────────

def fetch_arxiv_papers(arxiv_name, max_results=MAX_PER_SOURCE):
    """查询某作者近 48 小时内的 ArXiv 新论文"""
    if not arxiv_name:
        return []

    url = (
        f"http://export.arxiv.org/api/query"
        f"?search_query=au:{requests.utils.quote(arxiv_name)}"
        f"&sortBy=submittedDate&sortOrder=descending"
        f"&max_results=10"
    )
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [ArXiv] {arxiv_name} 请求失败: {e}")
        return []

    feed = feedparser.parse(resp.text)
    papers = []
    cutoff = WEEK_AGO.replace(tzinfo=None)  # feedparser 的 published_parsed 是 naive UTC

    for entry in feed.entries:
        published = entry.get("published_parsed")
        if published is None:
            # 尝试从 arxiv:published 或 updated 获取
            if hasattr(entry, "arxiv_published"):
                try:
                    published = time.strptime(entry.arxiv_published, "%Y-%m-%dT%H:%M:%SZ")
                except Exception:
                    continue
            else:
                continue

        pub_dt = datetime(*published[:6])
        if pub_dt < cutoff:
            continue

        # 提取 arxiv ID
        arxiv_id = entry.get("id", "").split("/abs/")[-1]
        arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
        title = entry.get("title", "Unknown").strip().replace("\n", " ")
        # 清理标题中多余的空白
        title = " ".join(title.split())

        papers.append({
            "title": title,
            "url": arxiv_url,
            "date": pub_dt.strftime("%Y-%m-%d"),
        })

    return papers


# ─── GitHub 动态采集 ────────────────────────────────────

def fetch_github_events(github_user, max_results=MAX_PER_SOURCE):
    """查询 GitHub 用户/组织近 7 天公开动态"""
    if not github_user:
        return []

    headers = {"Accept": "application/vnd.github+json", "User-Agent": "AI-News-Collector/1.0"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    # 判断是用户还是组织：先尝试 users endpoint
    url = f"https://api.github.com/users/{github_user}/events/public?per_page=20"

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 404:
            # 可能是组织，用 orgs endpoint
            url = f"https://api.github.com/orgs/{github_user}/events?per_page=20"
            resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [GitHub] {github_user} 请求失败: {e}")
        return []

    events = resp.json()
    if not isinstance(events, list):
        return []

    results = []
    cutoff = WEEK_AGO.replace(tzinfo=timezone.utc)
    seen = set()

    for ev in events:
        created_str = ev.get("created_at", "")
        if not created_str:
            continue

        try:
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        except Exception:
            continue

        if created < cutoff:
            continue

        desc = _format_github_event(ev)
        if not desc:
            continue

        repo_name = ev.get("repo", {}).get("name", "")
        event_url = f"https://github.com/{repo_name}"
        dedup_key = f"{desc}|{event_url}"
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        results.append({
            "description": desc,
            "url": event_url,
            "date": created.strftime("%Y-%m-%d %H:%M"),
        })

        if len(results) >= max_results:
            break

    return results


def _format_github_event(ev):
    """格式化 GitHub Event 为简短描述"""
    ev_type = ev.get("type", "")
    repo = ev.get("repo", {}).get("name", "")
    payload = ev.get("payload", {})

    if ev_type == "PushEvent":
        commits = payload.get("commits", [])
        n = len(commits)
        if n == 0:
            return None
        msg = commits[0].get("message", "").split("\n")[0][:60]
        if n == 1:
            return f"Push to {repo}: {msg}"
        return f"Push {n} commits to {repo}: {msg}"

    elif ev_type == "CreateEvent":
        ref_type = payload.get("ref_type", "branch")
        ref = payload.get("ref", "")
        return f"Created {ref_type} {ref} in {repo}"

    elif ev_type == "DeleteEvent":
        ref_type = payload.get("ref_type", "branch")
        ref = payload.get("ref", "")
        return f"Deleted {ref_type} {ref} in {repo}"

    elif ev_type == "WatchEvent":
        return f"Starred {repo}"

    elif ev_type == "ForkEvent":
        return f"Forked {repo}"

    elif ev_type == "IssuesEvent":
        action = payload.get("action", "")
        issue = payload.get("issue", {}).get("title", "")[:60]
        return f"{action.capitalize()} issue in {repo}: {issue}"

    elif ev_type == "IssueCommentEvent":
        issue = payload.get("issue", {}).get("title", "")[:60]
        return f"Commented on issue in {repo}: {issue}"

    elif ev_type == "PullRequestEvent":
        action = payload.get("action", "")
        pr = payload.get("pull_request", {}).get("title", "")[:60]
        return f"{action.capitalize()} PR in {repo}: {pr}"

    elif ev_type == "ReleaseEvent":
        release = payload.get("release", {}).get("name", "")
        return f"Released {release} in {repo}"

    elif ev_type == "PublicEvent":
        return f"Made {repo} public"

    else:
        return f"{ev_type} on {repo}"


# ─── Twitter 动态采集（需 TWITTER_BEARER_TOKEN）─────────

def fetch_twitter_tweets(twitter_id, max_results=MAX_PER_SOURCE):
    """查询 Twitter 用户最近推文（需 bearer token）"""
    if not twitter_id or not TWITTER_BEARER_TOKEN:
        return []

    url = f"https://api.twitter.com/2/users/{twitter_id}/tweets"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    params = {
        "max_results": max_results,
        "tweet.fields": "created_at",
        "exclude": "retweets,replies",
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [Twitter] {twitter_id} 请求失败: {e}")
        return []

    data = resp.json()
    tweets = data.get("data", [])
    results = []
    cutoff = YESTERDAY.replace(tzinfo=timezone.utc)

    for tw in tweets:
        created_str = tw.get("created_at", "")
        try:
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        except Exception:
            continue
        if created < cutoff:
            continue

        tw_id = tw.get("id", "")
        tw_url = f"https://twitter.com/i/status/{tw_id}"
        text = tw.get("text", "")[:120].replace("\n", " ")
        results.append({
            "description": text,
            "url": tw_url,
            "date": created.strftime("%Y-%m-%d %H:%M"),
        })

    return results[:max_results]


# ─── 微博动态采集（需 WEIBO_COOKIE）────────────────────

def fetch_weibo_posts(weibo_uid, max_results=MAX_PER_SOURCE):
    """查询微博用户最近动态（需 cookie）"""
    if not weibo_uid or not WEIBO_COOKIE:
        return []

    url = f"https://weibo.com/ajax/statuses/mymblog?uid={weibo_uid}&page=1&feature=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": WEIBO_COOKIE,
        "Referer": "https://weibo.com/",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [Weibo] {weibo_uid} 请求失败: {e}")
        return []

    try:
        data = resp.json()
    except Exception:
        return []

    posts = data.get("data", {}).get("list", [])
    results = []
    cutoff = YESTERDAY

    for post in posts:
        created_str = post.get("created_at", "")
        try:
            # 微博时间格式 "Thu Jul 02 09:00:00 +0800 2026"
            created = datetime.strptime(created_str, "%a %b %d %H:%M:%S %z %Y")
        except Exception:
            continue
        if created < cutoff:
            continue

        post_id = post.get("id", "") or post.get("mid", "")
        post_url = f"https://weibo.com/{weibo_uid}/{post_id}" if post_id else ""
        # 提取纯文本
        text_raw = post.get("text_raw", "") or post.get("text", "")
        # 去掉 HTML 标签
        import re
        text = re.sub(r"<[^>]+>", "", text_raw)[:120].strip()

        results.append({
            "description": text,
            "url": post_url,
            "date": created.strftime("%Y-%m-%d %H:%M"),
        })

    return results[:max_results]


# ─── 翻译 ───────────────────────────────────────────────

def contains_chinese(text):
    """判断文本是否包含中文"""
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def translate_batch(items, max_retries=2):
    """批量翻译 items 中的 description 字段（仅翻译不含中文的）"""
    from deep_translator import GoogleTranslator

    to_translate = []
    indices = []
    for i, item in enumerate(items):
        desc = item.get("description", "")
        if desc and not contains_chinese(desc):
            to_translate.append(desc)
            indices.append(i)

    if not to_translate:
        print("  所有内容已为中文，跳过翻译")
        return

    print(f"  待翻译 {len(to_translate)} 条英文内容...")
    results = []
    for text in to_translate:
        for attempt in range(max_retries):
            try:
                translated = GoogleTranslator(source="auto", target="zh-CN").translate(text)
                results.append(translated)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print(f"  翻译失败: {text[:40]}... → {e}")
                    results.append(text)  # 失败保留原文

    for idx, translated in zip(indices, results):
        items[idx]["translated"] = translated

    print(f"  翻译完成 {len(results)} 条")


# ─── 飞书推送 ───────────────────────────────────────────

def build_feishu_card(all_results):
    """构建飞书卡片消息"""
    header_text = f"AI圈大佬动态日报 | {TODAY}"
    elements = []

    # 统计总数
    total_papers = sum(1 for r in all_results if r["source"] == "ArXiv")
    total_github = sum(1 for r in all_results if r["source"] == "GitHub")
    total_twitter = sum(1 for r in all_results if r["source"] == "Twitter")
    total_weibo = sum(1 for r in all_results if r["source"] == "微博")

    # 摘要行
    summary_parts = []
    if total_papers:
        summary_parts.append(f"📄 论文 {total_papers} 篇")
    if total_github:
        summary_parts.append(f"💻 GitHub {total_github} 条")
    if total_twitter:
        summary_parts.append(f"🐦 Twitter {total_twitter} 条")
    if total_weibo:
        summary_parts.append(f"🌐 微博 {total_weibo} 条")

    summary = " | ".join(summary_parts) if summary_parts else "今日暂无新动态"

    elements.append({
        "tag": "div",
        "text": {"tag": "lark_md", "content": f"**{summary}**\n"},
    })

    # 按来源分组
    source_groups = [
        ("📄 ArXiv 最新论文", "ArXiv"),
        ("💻 GitHub 动态", "GitHub"),
        ("🐦 Twitter 动态", "Twitter"),
        ("🌐 微博动态", "微博"),
    ]

    for group_title, source in source_groups:
        group_items = [r for r in all_results if r["source"] == source]
        if not group_items:
            continue

        lines = [f"**{group_title}**\n"]
        for item in group_items:
            name = item["name"]
            desc = item.get("translated") or item["description"]
            desc = desc.replace("**", "").replace("*", "")
            url = item["url"]
            date = item.get("date", "")
            lines.append(f"- **{name}**: [{desc}]({url})  _{date}_")

        content = "\n".join(lines)
        # 飞书卡片单元素有内容长度限制，过长则拆分
        if len(content) > 4000:
            # 截断处理，每条单独发送的方式过于复杂，这里取前若干条
            content = content[:3800] + "\n... (内容过长已截断)"

        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": content},
        })
        elements.append({"tag": "hr"})

    # 移除最后一个多余的 hr
    if elements and elements[-1].get("tag") == "hr":
        elements.pop()

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": header_text},
                "template": "blue",
            },
            "elements": elements,
        },
    }

    # 估算卡片大小，飞书限制约 30KB
    card_json = json.dumps(card, ensure_ascii=False)
    if len(card_json) > 25000:
        # 降级为简单文本消息
        return build_feishu_text(all_results)

    return card


def build_feishu_text(all_results):
    """降级：使用富文本消息"""
    lines = [f"AI圈大佬动态日报 | {TODAY}", ""]

    source_groups = [
        ("📄 ArXiv 最新论文", "ArXiv"),
        ("💻 GitHub 动态", "GitHub"),
        ("🐦 Twitter 动态", "Twitter"),
        ("🌐 微博动态", "微博"),
    ]

    for group_title, source in source_groups:
        group_items = [r for r in all_results if r["source"] == source]
        if not group_items:
            continue

        lines.append(group_title)
        for item in group_items[:MAX_PER_SOURCE * 3]:  # 限制条数
            desc = item.get("translated") or item["description"]
            lines.append(
                f"  • {item['name']}: {desc[:100]}"
            )
        lines.append("")

    if not any(r for r in all_results):
        lines.append("今日暂无新动态")

    return {
        "msg_type": "text",
        "content": {"text": "\n".join(lines)},
    }


def send_to_feishu(card):
    """发送消息到飞书 webhook"""
    if not FEISHU_WEBHOOK_URL:
        print("❌ 未配置 FEISHU_WEBHOOK_URL，跳过推送")
        return False

    try:
        resp = requests.post(
            FEISHU_WEBHOOK_URL,
            json=card,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") == 0:
            print("✅ 飞书推送成功")
            return True
        else:
            print(f"❌ 飞书推送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 飞书推送异常: {e}")
        return False


# ─── 主流程 ─────────────────────────────────────────────

def main():
    print(f"=== AI圈大佬动态采集开始 ({TODAY}) ===")

    all_results = []

    for big in BIG_NAMES:
        name = big["name"]
        print(f"\n🔍 采集: {name}")

        # ArXiv 论文
        if big["arxiv_name"]:
            papers = fetch_arxiv_papers(big["arxiv_name"])
            for p in papers:
                p["name"] = name
                p["source"] = "ArXiv"
                all_results.append(p)
            print(f"  ArXiv: {len(papers)} 篇")
            time.sleep(1)  # 礼貌延迟，避免触发限流

        # GitHub 动态
        if big["github_user"]:
            events = fetch_github_events(big["github_user"])
            for e in events:
                e["name"] = f"{name} (@{big['github_user']})"
                e["source"] = "GitHub"
                all_results.append(e)
            print(f"  GitHub: {len(events)} 条")
            time.sleep(0.3)

        # Twitter
        if big["twitter_id"]:
            tweets = fetch_twitter_tweets(big["twitter_id"])
            for t in tweets:
                t["name"] = name
                t["source"] = "Twitter"
                all_results.append(t)
            print(f"  Twitter: {len(tweets)} 条")
            time.sleep(0.5)

        # 微博
        if big["weibo_uid"]:
            weibos = fetch_weibo_posts(big["weibo_uid"])
            for w in weibos:
                w["name"] = name
                w["source"] = "微博"
                all_results.append(w)
            print(f"  微博: {len(weibos)} 条")
            time.sleep(0.5)

    print(f"\n📊 总计采集 {len(all_results)} 条动态")

    # 翻译英文内容为中文
    if all_results:
        translate_batch(all_results)

    if not all_results:
        print("今日无新动态，仍发送空日报")
        card = build_feishu_text([])
    else:
        card = build_feishu_card(all_results)

    send_to_feishu(card)
    print("=== 采集完成 ===")


if __name__ == "__main__":
    main()
