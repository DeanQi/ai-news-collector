#!/usr/bin/env python3
"""
AIåå¤§ä½¬å¨ææ¥æ¥ééèæ¬
- éé ArXiv ææ°è®ºæ
- éé GitHub å¬å¼å¨æ
- éé Twitter å¨æï¼ééç½® TWITTER_BEARER_TOKENï¼
- ééå¾®åå¨æï¼ééç½® WEIBO_COOKIEï¼
- æ¨éå°é£ä¹¦æºå¨äºº Webhook
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

# âââ éç½® âââââââââââââââââââââââââââââââââââââââââââââââ

FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")
WEIBO_COOKIE = os.environ.get("WEIBO_COOKIE", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

BEIJING_TZ = pytz.timezone("Asia/Shanghai")
TODAY = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
YESTERDAY = (datetime.now(BEIJING_TZ) - timedelta(days=1))
WEEK_AGO = (datetime.now(BEIJING_TZ) - timedelta(days=7))

# æ¯ä¸ªæ°æ®æºæå¤å±ç¤ºæ¡æ°
MAX_PER_SOURCE = 1

# âââ å¤§ä½¬ä¿¡æ¯åº âââââââââââââââââââââââââââââââââââââââââ

# æ ¼å¼: { "name": "ä¸­æå/å¸¸ç¨å", "arxiv_name": "ArXivä½èå(Last, First)", "github_user": "GitHubç¨æ·åæorg", "twitter_id": "Twitterç¨æ·IDæ°å­", "twitter_username": "Twitterç¨æ·å", "weibo_uid": "å¾®åUID" }
BIG_NAMES = [
    # === é¡¶çº§ç ç©¶æºæ/ä¼ä¸é¢è¢ ===
    {"name": "Yann LeCun",           "arxiv_name": "LeCun, Yann",            "github_user": "",                   "twitter_id": "105943820",           "twitter_username": "ylecun",              "weibo_uid": ""},
    {"name": "Geoffrey Hinton",      "arxiv_name": "Hinton, Geoffrey",       "github_user": "",                   "twitter_id": "",                     "twitter_username": "geoffreyhinton",       "weibo_uid": ""},
    {"name": "Yoshua Bengio",        "arxiv_name": "Bengio, Yoshua",         "github_user": "",                   "twitter_id": "",                     "twitter_username": "yoshuabengio",         "weibo_uid": ""},
    {"name": "Ilya Sutskever",       "arxiv_name": "Sutskever, Ilya",        "github_user": "",                   "twitter_id": "",                     "twitter_username": "ilyasut",              "weibo_uid": ""},
    {"name": "Sam Altman",           "arxiv_name": "",                       "github_user": "",                   "twitter_id": "19497576",            "twitter_username": "sama",                "weibo_uid": ""},
    {"name": "Demis Hassabis",       "arxiv_name": "Hassabis, Demis",        "github_user": "",                   "twitter_id": "389534645",           "twitter_username": "demishassabis",       "weibo_uid": ""},
    {"name": "æé£é£ (Fei-Fei Li)",   "arxiv_name": "Li, Fei-Fei",            "github_user": "",                   "twitter_id": "978780836951838720",  "twitter_username": "drfeifei",             "weibo_uid": ""},
    {"name": "å´æ©è¾¾ (Andrew Ng)",    "arxiv_name": "Ng, Andrew",             "github_user": "andrewng",           "twitter_id": "823533",              "twitter_username": "AndrewYNg",            "weibo_uid": ""},

    # === å¤§æ¨¡å/LLMæ¹å ===
    {"name": "Andrej Karpathy",      "arxiv_name": "Karpathy, Andrej",       "github_user": "karpathy",           "twitter_id": "16539359",            "twitter_username": "karpathy",             "weibo_uid": ""},
    {"name": "Dario Amodei",         "arxiv_name": "Amodei, Dario",          "github_user": "",                   "twitter_id": "16668453",            "twitter_username": "DarioAmodei",          "weibo_uid": ""},
    {"name": "Aidan Gomez",          "arxiv_name": "Gomez, Aidan",           "github_user": "",                   "twitter_id": "2347577145",          "twitter_username": "aidan_mclau",          "weibo_uid": ""},
    {"name": "Noam Shazeer",         "arxiv_name": "Shazeer, Noam",          "github_user": "",                   "twitter_id": "",                     "twitter_username": "NoamShazeer",          "weibo_uid": ""},
    {"name": "æ¢æé (DeepSeek)",     "arxiv_name": "",                       "github_user": "deepseek-ai",        "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": ""},

    # === å¼æº/å·¥å·çæ ===
    {"name": "Clement Delangue",     "arxiv_name": "",                       "github_user": "ClementDelangue",    "twitter_id": "13260032",            "twitter_username": "ClementDelangue",      "weibo_uid": ""},
    {"name": "Thomas Wolf",          "arxiv_name": "",                       "github_user": "thomwolf",           "twitter_id": "14345915",            "twitter_username": "Thom_Wolf",            "weibo_uid": ""},
    {"name": "Lukas Biewald",        "arxiv_name": "",                       "github_user": "lukas",              "twitter_id": "13920962",            "twitter_username": "l2k",                  "weibo_uid": ""},

    # === ä¸­å½AIå ===
    {"name": "å¼ äºå¤",               "arxiv_name": "Zhang, Ya-Qin",           "github_user": "",                   "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": "1645171780"},
    {"name": "åæ° (æºè°±/ChatGLM)",   "arxiv_name": "Tang, Jie",              "github_user": "THUDM",              "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": "2126427211"},
    {"name": "çå°å· (ç¾å·æºè½)",     "arxiv_name": "",                       "github_user": "baichuan-inc",       "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": "1582488432"},
    {"name": "æå¼å¤ (é¶ä¸ä¸ç©)",     "arxiv_name": "Lee, Kai-Fu",            "github_user": "",                   "twitter_id": "21443430",            "twitter_username": "kaifulee",             "weibo_uid": "1197161814"},
    {"name": "å¨é¸¿ç¥ (360)",         "arxiv_name": "",                       "github_user": "",                   "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": "1708942053"},
    {"name": "é»ä»å (Jensen Huang)", "arxiv_name": "",                       "github_user": "",                   "twitter_id": "",                     "twitter_username": "JenHsun_Huang",        "weibo_uid": ""},

    # === å­¦æ¯åæ²¿ ===
    {"name": "Percy Liang",          "arxiv_name": "Liang, Percy",           "github_user": "",                   "twitter_id": "26749844",            "twitter_username": "percyliang",           "weibo_uid": ""},
    {"name": "Jim Fan",              "arxiv_name": "Fan, Jim",               "github_user": "",                   "twitter_id": "1203899672",          "twitter_username": "DrJimFan",             "weibo_uid": ""},
    {"name": "Christopher Manning",  "arxiv_name": "Manning, Christopher",   "github_user": "",                   "twitter_id": "46721826",            "twitter_username": "chrmanning",           "weibo_uid": ""},
    {"name": "Pieter Abbeel",        "arxiv_name": "Abbeel, Pieter",         "github_user": "",                   "twitter_id": "105943362",           "twitter_username": "pabbeel",              "weibo_uid": ""},
    {"name": "Sergey Levine",        "arxiv_name": "Levine, Sergey",         "github_user": "",                   "twitter_id": "3352472124",          "twitter_username": "svlevine",             "weibo_uid": ""},

    # === éè¦ç»ç»/å¢é ===
    {"name": "Meta FAIR",            "arxiv_name": "",                       "github_user": "facebookresearch",   "twitter_id": "14825531",            "twitter_username": "MetaAI",               "weibo_uid": ""},
    {"name": "Google DeepMind",      "arxiv_name": "",                       "github_user": "google-deepmind",    "twitter_id": "1317668457",          "twitter_username": "GoogleDeepMind",       "weibo_uid": ""},
    {"name": "OpenAI",               "arxiv_name": "",                       "github_user": "openai",             "twitter_id": "4398626122",          "twitter_username": "OpenAI",               "weibo_uid": ""},
    {"name": "Anthropic",            "arxiv_name": "",                       "github_user": "anthropics",         "twitter_id": "1405248728",          "twitter_username": "AnthropicAI",          "weibo_uid": ""},
    {"name": "Cohere",               "arxiv_name": "",                       "github_user": "cohere-ai",          "twitter_id": "1240398540438073344", "twitter_username": "cohere",               "weibo_uid": ""},
    {"name": "HuggingFace",          "arxiv_name": "",                       "github_user": "huggingface",        "twitter_id": "1078992647933444096", "twitter_username": "huggingface",          "weibo_uid": ""},
]


# âââ ArXiv è®ºæéé ââââââââââââââââââââââââââââââââââââ

def fetch_arxiv_papers(arxiv_name, max_results=MAX_PER_SOURCE):
    """æ¥è¯¢æä½èè¿ 48 å°æ¶åç ArXiv æ°è®ºæ"""
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
        print(f"  [ArXiv] {arxiv_name} è¯·æ±å¤±è´¥: {e}")
        return []

    feed = feedparser.parse(resp.text)
    papers = []
    cutoff = WEEK_AGO.replace(tzinfo=None)  # feedparser ç published_parsed æ¯ naive UTC

    for entry in feed.entries:
        published = entry.get("published_parsed")
        if published is None:
            # å°è¯ä» arxiv:published æ updated è·å
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

        # æå arxiv ID
        arxiv_id = entry.get("id", "").split("/abs/")[-1]
        arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
        title = entry.get("title", "Unknown").strip().replace("\n", " ")
        # æ¸çæ é¢ä¸­å¤ä½çç©ºç½
        title = " ".join(title.split())

        papers.append({
            "title": title,
            "url": arxiv_url,
            "date": pub_dt.strftime("%Y-%m-%d"),
        })

    return papers


# âââ GitHub å¨æéé ââââââââââââââââââââââââââââââââââââ

def fetch_github_events(github_user, max_results=MAX_PER_SOURCE):
    """æ¥è¯¢ GitHub ç¨æ·/ç»ç»è¿ 7 å¤©å¬å¼å¨æ"""
    if not github_user:
        return []

    headers = {"Accept": "application/vnd.github+json", "User-Agent": "AI-News-Collector/1.0"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    # å¤æ­æ¯ç¨æ·è¿æ¯ç»ç»ï¼åå°è¯ users endpoint
    url = f"https://api.github.com/users/{github_user}/events/public?per_page=20"

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 404:
            # å¯è½æ¯ç»ç»ï¼ç¨ orgs endpoint
            url = f"https://api.github.com/orgs/{github_user}/events?per_page=20"
            resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [GitHub] {github_user} è¯·æ±å¤±è´¥: {e}")
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
    """æ ¼å¼å GitHub Event ä¸ºç®ç­æè¿°"""
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


# âââ Twitter å¨æééï¼é TWITTER_BEARER_TOKENï¼âââââââââ

def fetch_twitter_rss(twitter_username, max_results=MAX_PER_SOURCE):
    """éè¿ Nitter RSS è·åæ¨æï¼Twitter API ä¸å¯ç¨æ¶çéçº§æ¹æ¡ï¼"""
    if not twitter_username:
        return []

    rss_urls = [
        f"https://nitter.poast.org/{twitter_username}/rss",
        f"https://nitter.privacydev.net/{twitter_username}/rss",
    ]

    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    results = []

    for rss_url in rss_urls:
        try:
            resp = requests.get(rss_url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"  [Nitter RSS] {rss_url} è¯·æ±å¤±è´¥: {e}")
            continue

        try:
            root = ET.fromstring(resp.text)
        except ET.ParseError as e:
            print(f"  [Nitter RSS] XML è§£æå¤±è´¥: {e}")
            continue

        # RSS 2.0 æ ¼å¼: channel -> item
        for item in root.iter("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            pub_date_el = item.find("pubDate")

            title = title_el.text if title_el is not None else ""
            link = link_el.text if link_el is not None else ""
            pub_date_str = pub_date_el.text if pub_date_el is not None else ""

            if not title or not link:
                continue

            # è§£æ pubDateï¼RFC 2822 æ ¼å¼: "Thu, 03 Jul 2026 12:00:00 GMT"ï¼
            try:
                pub_dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
                pub_dt = pub_dt.replace(tzinfo=timezone.utc)
            except Exception:
                # å°è¯ä¸å¸¦ææçæ ¼å¼
                try:
                    pub_dt = datetime.strptime(pub_date_str, "%d %b %Y %H:%M:%S %Z")
                    pub_dt = pub_dt.replace(tzinfo=timezone.utc)
                except Exception:
                    continue

            if pub_dt < cutoff:
                continue

            text = title.strip().replace("\n", " ")
            results.append({
                "description": text[:120],
                "url": link,
                "date": pub_dt.strftime("%Y-%m-%d %H:%M"),
                "source": "twitter_rss",
            })

        # æåè·åå°æ°æ®å°±è·³åº
        if results:
            break

    return results[:max_results]


def fetch_twitter_tweets(twitter_id, twitter_username="", max_results=MAX_PER_SOURCE):
    """æ¥è¯¢ Twitter ç¨æ·æè¿æ¨æï¼é bearer tokenï¼ï¼API ä¸å¯ç¨æ¶èªå¨éçº§å° Nitter RSS"""
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
        if resp.status_code in (402, 403, 429):
            print(f"  Twitter API ä¸å¯ç¨(ç¶æç :{resp.status_code})ï¼éçº§å° Nitter RSS for @{twitter_username}")
            return fetch_twitter_rss(twitter_username, max_results)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status_code = resp.status_code if resp is not None else 0
        # æ£æ¥æ¯å¦å·²ç»è¢«ä¸é¢ç if ææè¿ï¼çè®ºä¸ä¸ä¼èµ°å°è¿éï¼ä½ä¿çååºï¼
        if status_code in (402, 403, 429):
            print(f"  Twitter API ä¸å¯ç¨(ç¶æç :{status_code})ï¼éçº§å° Nitter RSS for @{twitter_username}")
            return fetch_twitter_rss(twitter_username, max_results)
        raise
    except Exception as e:
        print(f"  [Twitter] {twitter_id} è¯·æ±å¤±è´¥: {e}")
        if twitter_username:
            print(f"  éçº§å° Nitter RSS for @{twitter_username}")
            return fetch_twitter_rss(twitter_username, max_results)
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


# âââ å¾®åå¨æééï¼é WEIBO_COOKIEï¼ââââââââââââââââââââ

def fetch_weibo_posts(weibo_uid, max_results=MAX_PER_SOURCE):
    """æ¥è¯¢å¾®åç¨æ·æè¿å¨æï¼é cookieï¼"""
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
        print(f"  [Weibo] {weibo_uid} è¯·æ±å¤±è´¥: {e}")
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
            # å¾®åæ¶é´æ ¼å¼ "Thu Jul 02 09:00:00 +0800 2026"
            created = datetime.strptime(created_str, "%a %b %d %H:%M:%S %z %Y")
        except Exception:
            continue
        if created < cutoff:
            continue

        post_id = post.get("id", "") or post.get("mid", "")
        post_url = f"https://weibo.com/{weibo_uid}/{post_id}" if post_id else ""
        # æåçº¯ææ¬
        text_raw = post.get("text_raw", "") or post.get("text", "")
        # å»æ HTML æ ç­¾
        import re
        text = re.sub(r"<[^>]+>", "", text_raw)[:120].strip()

        results.append({
            "description": text,
            "url": post_url,
            "date": created.strftime("%Y-%m-%d %H:%M"),
        })

    return results[:max_results]


# âââ ç¿»è¯ âââââââââââââââââââââââââââââââââââââââââââââââ

def contains_chinese(text):
    """å¤æ­ææ¬æ¯å¦åå«ä¸­æ"""
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def translate_batch(items, max_retries=2):
    """æ¹éç¿»è¯ items ä¸­ç description å­æ®µï¼ä»ç¿»è¯ä¸å«ä¸­æçï¼"""
    from deep_translator import GoogleTranslator

    to_translate = []
    indices = []
    for i, item in enumerate(items):
        desc = item.get("description", "")
        if desc and not contains_chinese(desc):
            to_translate.append(desc)
            indices.append(i)

    if not to_translate:
        print("  ææåå®¹å·²ä¸ºä¸­æï¼è·³è¿ç¿»è¯")
        return

    print(f"  å¾ç¿»è¯ {len(to_translate)} æ¡è±æåå®¹...")
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
                    print(f"  ç¿»è¯å¤±è´¥: {text[:40]}... â {e}")
                    results.append(text)  # å¤±è´¥ä¿çåæ

    for idx, translated in zip(indices, results):
        items[idx]["translated"] = translated

    print(f"  ç¿»è¯å®æ {len(results)} æ¡")


# âââ é£ä¹¦æ¨é âââââââââââââââââââââââââââââââââââââââââââ

def build_feishu_card(all_results):
    """æå»ºé£ä¹¦å¡çæ¶æ¯"""
    header_text = f"AIåå¤§ä½¬å¨ææ¥æ¥ | {TODAY}"
    elements = []

    # ç»è®¡æ»æ°
    total_papers = sum(1 for r in all_results if r["source"] == "ArXiv")
    total_github = sum(1 for r in all_results if r["source"] == "GitHub")
    total_twitter = sum(1 for r in all_results if r["source"] == "Twitter")
    total_weibo = sum(1 for r in all_results if r["source"] == "å¾®å")

    # æè¦è¡
    summary_parts = []
    if total_papers:
        summary_parts.append(f"ð è®ºæ {total_papers} ç¯")
    if total_github:
        summary_parts.append(f"ð» GitHub {total_github} æ¡")
    if total_twitter:
        summary_parts.append(f"ð¦ Twitter {total_twitter} æ¡")
    if total_weibo:
        summary_parts.append(f"ð å¾®å {total_weibo} æ¡")

    summary = " | ".join(summary_parts) if summary_parts else "ä»æ¥ææ æ°å¨æ"

    elements.append({
        "tag": "div",
        "text": {"tag": "lark_md", "content": f"**{summary}**\n"},
    })

    # ææ¥æºåç»
    source_groups = [
        ("ð ArXiv ææ°è®ºæ", "ArXiv"),
        ("ð» GitHub å¨æ", "GitHub"),
        ("ð¦ Twitter å¨æ", "Twitter"),
        ("ð å¾®åå¨æ", "å¾®å"),
    ]

    for group_title, source in source_groups:
        group_items = [r for r in all_results if r["source"] == source]
        if not group_items:
            continue

        lines = [f"**{group_title}**\n"]
        for item in group_items:
            name = item["name"]
            desc = item.get("translated") or item.get("description", "")
            desc = desc.replace("**", "").replace("*", "")
            url = item["url"]
            date = item.get("date", "")
            lines.append(f"- **{name}**: [{desc}]({url})  _{date}_")

        content = "\n".join(lines)
        # é£ä¹¦å¡çååç´ æåå®¹é¿åº¦éå¶ï¼è¿é¿åæå
        if len(content) > 4000:
            # æªæ­å¤çï¼æ¯æ¡åç¬åéçæ¹å¼è¿äºå¤æï¼è¿éååè¥å¹²æ¡
            content = content[:3800] + "\n... (åå®¹è¿é¿å·²æªæ­)"

        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": content},
        })
        elements.append({"tag": "hr"})

    # ç§»é¤æåä¸ä¸ªå¤ä½ç hr
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

    # ä¼°ç®å¡çå¤§å°ï¼é£ä¹¦éå¶çº¦ 30KB
    card_json = json.dumps(card, ensure_ascii=False)
    if len(card_json) > 25000:
        # éçº§ä¸ºç®åææ¬æ¶æ¯
        return build_feishu_text(all_results)

    return card


def build_feishu_text(all_results):
    """éçº§ï¼ä½¿ç¨å¯ææ¬æ¶æ¯"""
    lines = [f"AIåå¤§ä½¬å¨ææ¥æ¥ | {TODAY}", ""]

    source_groups = [
        ("ð ArXiv ææ°è®ºæ", "ArXiv"),
        ("ð» GitHub å¨æ", "GitHub"),
        ("ð¦ Twitter å¨æ", "Twitter"),
        ("ð å¾®åå¨æ", "å¾®å"),
    ]

    for group_title, source in source_groups:
        group_items = [r for r in all_results if r["source"] == source]
        if not group_items:
            continue

        lines.append(group_title)
        for item in group_items[:MAX_PER_SOURCE * 3]:  # éå¶æ¡æ°
            desc = item.get("translated") or item.get("description", "")
            lines.append(
                f"  â¢ {item['name']}: {desc[:100]}"
            )
        lines.append("")

    if not any(r for r in all_results):
        lines.append("ä»æ¥ææ æ°å¨æ")

    return {
        "msg_type": "text",
        "content": {"text": "\n".join(lines)},
    }


def send_to_feishu(card):
    """åéæ¶æ¯å°é£ä¹¦ webhook"""
    if not FEISHU_WEBHOOK_URL:
        print("â æªéç½® FEISHU_WEBHOOK_URLï¼è·³è¿æ¨é")
        return False

    try:
        resp = requests.post(
            FEISHU_WEBHOOK_URL,
            data=json.dumps(card, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=15,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") == 0:
            print("â é£ä¹¦æ¨éæå")
            return True
        else:
            print(f"â é£ä¹¦æ¨éå¤±è´¥: {result}")
            return False
    except Exception as e:
        print(f"â é£ä¹¦æ¨éå¼å¸¸: {e}")
        return False


# âââ ä¸»æµç¨ âââââââââââââââââââââââââââââââââââââââââââââ

def main():
    print(f"=== AIåå¤§ä½¬å¨æééå¼å§ ({TODAY}) ===")

    all_results = []

    for big in BIG_NAMES:
        name = big["name"]
        print(f"\nð éé: {name}")

        # ArXiv è®ºæ
        if big["arxiv_name"]:
            papers = fetch_arxiv_papers(big["arxiv_name"])
            for p in papers:
                p["name"] = name
                p["source"] = "ArXiv"
                all_results.append(p)
            print(f"  ArXiv: {len(papers)} ç¯")
            time.sleep(1)  # ç¤¼è²å»¶è¿ï¼é¿åè§¦åéæµ

        # GitHub å¨æ
        if big["github_user"]:
            events = fetch_github_events(big["github_user"])
            for e in events:
                e["name"] = f"{name} (@{big['github_user']})"
                e["source"] = "GitHub"
                all_results.append(e)
            print(f"  GitHub: {len(events)} æ¡")
            time.sleep(0.3)

        # Twitter
        if big["twitter_id"]:
            tweets = fetch_twitter_tweets(big["twitter_id"], big.get("twitter_username", ""))
            for t in tweets:
                t["name"] = name
                t["source"] = "Twitter"
                all_results.append(t)
            print(f"  Twitter: {len(tweets)} æ¡")
            time.sleep(0.5)

        # å¾®å
        if big["weibo_uid"]:
            weibos = fetch_weibo_posts(big["weibo_uid"])
            for w in weibos:
                w["name"] = name
                w["source"] = "å¾®å"
                all_results.append(w)
            print(f"  å¾®å: {len(weibos)} æ¡")
            time.sleep(0.5)

    print(f"\nð æ»è®¡éé {len(all_results)} æ¡å¨æ")

    # ç¿»è¯è±æåå®¹ä¸ºä¸­æ
    if all_results:
        translate_batch(all_results)

    if not all_results:
        print("ä»æ¥æ æ°å¨æï¼ä»åéç©ºæ¥æ¥")
        card = build_feishu_text([])
    else:
        card = build_feishu_card(all_results)

    send_to_feishu(card)
    print("=== ééå®æ ===")


if __name__ == "__main__":
    main()
