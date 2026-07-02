#!/usr/bin/env python3
"""
AIé¦å ãæµ£îå§©é¬ä½¹æ£©é¶ã©å°éåå¼é?- é²å¬æ³¦ ArXiv éâ¬éæîé?- é²å¬æ³¦ GitHub éîç´éã¦â¬?- é²å¬æ³¦ Twitter éã¦â¬ä¾ç´éâ¬é°å¶ç TWITTER_BEARER_TOKENé?- é²å¬æ³¦å¯°î¼å´¥éã¦â¬ä¾ç´éâ¬é°å¶ç WEIBO_COOKIEé?- éºã©â¬ä½¸åæ¤ç°åéåæ«æµ?Webhook
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

# é¹â¬é¹â¬é¹â¬ é°å¶ç é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬

FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")
WEIBO_COOKIE = os.environ.get("WEIBO_COOKIE", "")

BEIJING_TZ = pytz.timezone("Asia/Shanghai")
TODAY = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
YESTERDAY = (datetime.now(BEIJING_TZ) - timedelta(days=1))

# å§£å¿ééçåµå©§æ­æ¸¶æ¾¶æ°¬çç»çæ½¯é?MAX_PER_SOURCE = 1

# é¹â¬é¹â¬é¹â¬ æ¾¶Ñæµæ·âä¼æ´?é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬

# éçç´¡: { "name": "æ¶îæé?ç¯å¥æ¤é?, "arxiv_name": "ArXivæµ£æ»â¬å­æ(Last, First)", "github_user": "GitHubé¢ã¦åéå¶å¨org", "twitter_id": "Twitteré¢ã¦åIDéæ¿ç§", "weibo_uid": "å¯°î¼å´¥UID" }
BIG_NAMES = [
    # === æ¤¤åéªé®æâéçç¯/æµ¼ä½·ç¬æ£°åî» ===
    {"name": "Yann LeCun",           "arxiv_name": "LeCun, Yann",            "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Geoffrey Hinton",      "arxiv_name": "Hinton, Geoffrey",       "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Yoshua Bengio",        "arxiv_name": "Bengio, Yoshua",         "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Ilya Sutskever",       "arxiv_name": "Sutskever, Ilya",        "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Sam Altman",           "arxiv_name": "",                       "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Demis Hassabis",       "arxiv_name": "Hassabis, Demis",        "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "éåº¨î£æ¤?(Fei-Fei Li)",   "arxiv_name": "Li, Fei-Fei",            "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "éå­ä»¼æ?(Andrew Ng)",    "arxiv_name": "Ng, Andrew",             "github_user": "andrewng",           "twitter_id": "", "weibo_uid": ""},

    # === æ¾¶ÑÄé¨?LLMéç°æ ===
    {"name": "Andrej Karpathy",      "arxiv_name": "Karpathy, Andrej",       "github_user": "karpathy",           "twitter_id": "", "weibo_uid": ""},
    {"name": "Dario Amodei",         "arxiv_name": "Amodei, Dario",          "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Aidan Gomez",          "arxiv_name": "Gomez, Aidan",           "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Noam Shazeer",         "arxiv_name": "Shazeer, Noam",          "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "å§ä½¹æé¿?(DeepSeek)",     "arxiv_name": "",                       "github_user": "deepseek-ai",        "twitter_id": "", "weibo_uid": ""},

    # === å¯®â¬å©§?å®¸ã¥å¿é¢ç¸â¬?===
    {"name": "Clement Delangue",     "arxiv_name": "",                       "github_user": "ClementDelangue",    "twitter_id": "", "weibo_uid": ""},
    {"name": "Thomas Wolf",          "arxiv_name": "",                       "github_user": "thomwolf",           "twitter_id": "", "weibo_uid": ""},
    {"name": "Lukas Biewald",        "arxiv_name": "",                       "github_user": "lukas",              "twitter_id": "", "weibo_uid": ""},

    # === æ¶îæµAIé¦?===
    {"name": "å¯®ç±ç°¹é?,               "arxiv_name": "Zhang, Ya-Qin",           "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "éæ­æ¾ (éé¸¿æ°¨/ChatGLM)",   "arxiv_name": "Tang, Jie",              "github_user": "THUDM",              "twitter_id": "", "weibo_uid": ""},
    {"name": "éå¬ªç¬å®¸?(é§æ§çªéé¸¿å)",     "arxiv_name": "",                       "github_user": "baichuan-inc",       "twitter_id": "", "weibo_uid": ""},
    {"name": "éåº¡ç´æ¾¶?(éæµç«´æ¶å©å¢¿)",     "arxiv_name": "Lee, Kai-Fu",            "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "éã©ç¼ç»?(360)",         "arxiv_name": "",                       "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "æ¦åªç²é?(Jensen Huang)", "arxiv_name": "",                       "github_user": "",                   "twitter_id": "", "weibo_uid": ""},

    # === çï¸½æ¹³éå¶é¨ ===
    {"name": "Percy Liang",          "arxiv_name": "Liang, Percy",           "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Jim Fan",              "arxiv_name": "Fan, Jim",               "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Christopher Manning",  "arxiv_name": "Manning, Christopher",   "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Pieter Abbeel",        "arxiv_name": "Abbeel, Pieter",         "github_user": "",                   "twitter_id": "", "weibo_uid": ""},
    {"name": "Sergey Levine",        "arxiv_name": "Levine, Sergey",         "github_user": "",                   "twitter_id": "", "weibo_uid": ""},

    # === é²å¶î¦ç¼å­ç²/é¥ã¤æ§¦ ===
    {"name": "Meta FAIR",            "arxiv_name": "",                       "github_user": "facebookresearch",   "twitter_id": "", "weibo_uid": ""},
    {"name": "Google DeepMind",      "arxiv_name": "",                       "github_user": "google-deepmind",    "twitter_id": "", "weibo_uid": ""},
    {"name": "OpenAI",               "arxiv_name": "",                       "github_user": "openai",             "twitter_id": "", "weibo_uid": ""},
    {"name": "Anthropic",            "arxiv_name": "",                       "github_user": "anthropics",         "twitter_id": "", "weibo_uid": ""},
    {"name": "Cohere",               "arxiv_name": "",                       "github_user": "cohere-ai",          "twitter_id": "", "weibo_uid": ""},
    {"name": "HuggingFace",          "arxiv_name": "",                       "github_user": "huggingface",        "twitter_id": "", "weibo_uid": ""},
]


# é¹â¬é¹â¬é¹â¬ ArXiv ççæé²å¬æ³¦ é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬

def fetch_arxiv_papers(arxiv_name, max_results=MAX_PER_SOURCE):
    """éã¨îéæªç¶é°å°ç¹ 48 çå¿æ¤éå¯æ® ArXiv éæîé?""
    if not arxiv_name:
        return []

    url = (
        f"http://export.arxiv.org/api/query"
        f"?search_query=au:{requests.utils.quote(arxiv_name)}"
        f"&sortBy=submittedDate&sortOrder=descending"
        f"&max_results={max_results}"
    )
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [ArXiv] {arxiv_name} çéç°æ¾¶è¾«è§¦: {e}")
        return []

    feed = feedparser.parse(resp.text)
    papers = []
    cutoff = YESTERDAY.replace(tzinfo=None)  # feedparser é¨?published_parsed é?naive UTC

    for entry in feed.entries:
        published = entry.get("published_parsed")
        if published is None:
            # çæ¿ç¯æµ ?arxiv:published é´?updated é¾å³°å½
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

        # é»æ¬å½ arxiv ID
        arxiv_id = entry.get("id", "").split("/abs/")[-1]
        arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
        title = entry.get("title", "Unknown").strip().replace("\n", " ")
        # å¨å¯æéå¬î½æ¶îî¿æµ£æ¬æ®ç»è¹æ«§
        title = " ".join(title.split())

        papers.append({
            "title": title,
            "url": arxiv_url,
            "date": pub_dt.strftime("%Y-%m-%d"),
        })

    return papers


# é¹â¬é¹â¬é¹â¬ GitHub éã¦â¬ä¾å°é?é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬

def fetch_github_events(github_user, max_results=MAX_PER_SOURCE):
    """éã¨î GitHub é¢ã¦å/ç¼å­ç²æ©?48h éîç´éã¦â¬?""
    if not github_user:
        return []

    # éãæéîæ¤é´ç¯ç¹éîç²ç¼å·ç´°éå ç¾ç?users endpoint
    url = f"https://api.github.com/users/{github_user}/events/public?per_page={max_results * 3}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "AI-News-Collector/1.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 404:
            # éîåéîç²ç¼å·ç´é¢?orgs endpoint
            url = f"https://api.github.com/orgs/{github_user}/events?per_page={max_results * 3}"
            resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [GitHub] {github_user} çéç°æ¾¶è¾«è§¦: {e}")
        return []

    events = resp.json()
    if not isinstance(events, list):
        return []

    results = []
    cutoff = YESTERDAY.replace(tzinfo=timezone.utc)
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
    """éçç´¡é?GitHub Event æ¶è¹çé­îå¼¿æ©?""
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


# é¹â¬é¹â¬é¹â¬ Twitter éã¦â¬ä¾å°éå­ç´éâ¬ TWITTER_BEARER_TOKENéå¤æ¢é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬

def fetch_twitter_tweets(twitter_id, max_results=MAX_PER_SOURCE):
    """éã¨î Twitter é¢ã¦åéâ¬æ©æå¸¹éå·ç´éâ¬ bearer tokené?""
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
        print(f"  [Twitter] {twitter_id} çéç°æ¾¶è¾«è§¦: {e}")
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


# é¹â¬é¹â¬é¹â¬ å¯°î¼å´¥éã¦â¬ä¾å°éå­ç´éâ¬ WEIBO_COOKIEéå¤æ¢é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬

def fetch_weibo_posts(weibo_uid, max_results=MAX_PER_SOURCE):
    """éã¨îå¯°î¼å´¥é¢ã¦åéâ¬æ©æå§©é¬ä¾ç´éâ¬ cookieé?""
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
        print(f"  [Weibo] {weibo_uid} çéç°æ¾¶è¾«è§¦: {e}")
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
            # å¯°î¼å´¥éå æ£¿éçç´¡ "Thu Jul 02 09:00:00 +0800 2026"
            created = datetime.strptime(created_str, "%a %b %d %H:%M:%S %z %Y")
        except Exception:
            continue
        if created < cutoff:
            continue

        post_id = post.get("id", "") or post.get("mid", "")
        post_url = f"https://weibo.com/{weibo_uid}/{post_id}" if post_id else ""
        # é»æ¬å½ç»¾îæé?        text_raw = post.get("text_raw", "") or post.get("text", "")
        # éç»å¸ HTML éå©î·
        import re
        text = re.sub(r"<[^>]+>", "", text_raw)[:120].strip()

        results.append({
            "description": text,
            "url": post_url,
            "date": created.strftime("%Y-%m-%d %H:%M"),
        })

    return results[:max_results]


# é¹â¬é¹â¬é¹â¬ ç¼æç§ é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬

def contains_chinese(text):
    """éãæéå¨æ¹°éîæéå­ææ¶îæ"""
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def translate_batch(items, max_retries=2):
    """éµå½åºç¼æç§ items æ¶î æ® description çæ¥îéå ç²ç¼æç§æ¶å¶ææ¶îæé¨å¶ç´"""
    from deep_translator import GoogleTranslator

    to_translate = []
    indices = []
    for i, item in enumerate(items):
        desc = item.get("description", "")
        if desc and not contains_chinese(desc):
            to_translate.append(desc)
            indices.append(i)

    if not to_translate:
        print("  éµâ¬éå¤å´ç¹ç°å¡æ¶è½°èéå·ç´çºå® ç¹ç¼æç§")
        return

    print(f"  å¯°å¯çç?{len(to_translate)} éÂ¤å«³éå§å´ç¹?..")
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
                    print(f"  ç¼æç§æ¾¶è¾«è§¦: {text[:40]}... é«?{e}")
                    results.append(text)  # æ¾¶è¾«è§¦æ·æ¿æéç¸æ

    for idx, translated in zip(indices, results):
        items[idx]["translated"] = translated

    print(f"  ç¼æç§ç¹å±¾å {len(results)} é?)


# é¹â¬é¹â¬é¹â¬ æ¤ç°åéºã©â¬?é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬

def build_feishu_card(all_results):
    """éå«ç¼æ¤ç°åéï¼å¢å¨å ä¼"""
    header_text = f"AIé¦å ãæµ£îå§©é¬ä½¹æ£©é¶?| {TODAY}"
    elements = []

    # ç¼ç»î¸é¬ç»æ
    total_papers = sum(1 for r in all_results if r["source"] == "ArXiv")
    total_github = sum(1 for r in all_results if r["source"] == "GitHub")
    total_twitter = sum(1 for r in all_results if r["source"] == "Twitter")
    total_weibo = sum(1 for r in all_results if r["source"] == "å¯°î¼å´¥")

    # é½æ¨¿î¦ç?    summary_parts = []
    if total_papers:
        summary_parts.append(f"é¦æ« ççæ {total_papers} ç»¡?)
    if total_github:
        summary_parts.append(f"é¦æ GitHub {total_github} é?)
    if total_twitter:
        summary_parts.append(f"é¦æ Twitter {total_twitter} é?)
    if total_weibo:
        summary_parts.append(f"é¦å¯ª å¯°î¼å´¥ {total_weibo} é?)

    summary = " | ".join(summary_parts) if summary_parts else "æµ å©æ£©éåæ£¤éæ¿å§©é¬?

    elements.append({
        "tag": "div",
        "text": {"tag": "lark_md", "content": f"**{summary}**\n"},
    })

    # é¸å¤æ½µå©§æ¬åç¼?    source_groups = [
        ("é¦æ« ArXiv éâ¬éæîé?, "ArXiv"),
        ("é¦æ GitHub éã¦â¬?, "GitHub"),
        ("é¦æ Twitter éã¦â¬?, "Twitter"),
        ("é¦å¯ª å¯°î¼å´¥éã¦â¬?, "å¯°î¼å´¥"),
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
        # æ¤ç°åéï¼å¢éæåç»±ç³æ¹éå­îéå®å®³éæ¬åéå²ç¹éå®å¯é·åå
        if len(content) > 4000:
            # é´îææ¾¶å­æéå±¾ç¡éâ³å´éîå½é«ä½ºæ®éç°ç´¡æ©å¦ç°¬æ¾¶å¶æ½éå²ç¹é²å±½å½éå¶å«¢éªåæ½¯
            content = content[:3800] + "\n... (éå­îæ©å¬æ±å®¸ååé?"

        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": content},
        })
        elements.append({"tag": "hr"})

    # ç»å©æ«éâ¬éåºç«´æ¶îî¿æµ£æ¬æ® hr
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

    # æµ¼æ®ç»éï¼å¢æ¾¶Ñç¬éå²î£æ¶ï¹æªºéåå®³ 30KB
    card_json = json.dumps(card, ensure_ascii=False)
    if len(card_json) > 25000:
        # éå¶éªæ¶è¹çéææéîç§·é­?        return build_feishu_text(all_results)

    return card


def build_feishu_text(all_results):
    """éå¶éªéæ°«å¨é¢ã¥çéå¨æ¹°å¨å ä¼"""
    lines = [f"AIé¦å ãæµ£îå§©é¬ä½¹æ£©é¶?| {TODAY}", ""]

    source_groups = [
        ("é¦æ« ArXiv éâ¬éæîé?, "ArXiv"),
        ("é¦æ GitHub éã¦â¬?, "GitHub"),
        ("é¦æ Twitter éã¦â¬?, "Twitter"),
        ("é¦å¯ª å¯°î¼å´¥éã¦â¬?, "å¯°î¼å´¥"),
    ]

    for group_title, source in source_groups:
        group_items = [r for r in all_results if r["source"] == source]
        if not group_items:
            continue

        lines.append(group_title)
        for item in group_items[:MAX_PER_SOURCE * 3]:  # éæ¬åéâæ
            desc = item.get("translated") or item["description"]
            lines.append(
                f"  é¥?{item['name']}: {desc[:100]}"
            )
        lines.append("")

    if not any(r for r in all_results):
        lines.append("æµ å©æ£©éåæ£¤éæ¿å§©é¬?)

    return {
        "msg_type": "text",
        "text": {"content": "\n".join(lines)},
    }


def send_to_feishu(card):
    """éæ¦â¬ä½¹ç§·é­îåæ¤ç°å webhook"""
    if not FEISHU_WEBHOOK_URL:
        print("é?éîå¤ç¼?FEISHU_WEBHOOK_URLéå²ç¦æ©å¨å¸¹é«?)
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
            print("é?æ¤ç°åéºã©â¬ä½¹åé?)
            return True
        else:
            print(f"é?æ¤ç°åéºã©â¬ä½¸ãç? {result}")
            return False
    except Exception as e:
        print(f"é?æ¤ç°åéºã©â¬ä½¸ç´ç¯? {e}")
        return False


# é¹â¬é¹â¬é¹â¬ æ¶ç»ç¥¦ç»?é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬é¹â¬

def main():
    print(f"=== AIé¦å ãæµ£îå§©é¬ä¾å°éåç´æ¿®?({TODAY}) ===")

    all_results = []

    for big in BIG_NAMES:
        name = big["name"]
        print(f"\né¦æ³ é²å¬æ³¦: {name}")

        # ArXiv ççæ
        if big["arxiv_name"]:
            papers = fetch_arxiv_papers(big["arxiv_name"])
            for p in papers:
                p["name"] = name
                p["source"] = "ArXiv"
                all_results.append(p)
            print(f"  ArXiv: {len(papers)} ç»¡?)
            time.sleep(1)  # ç»è°çå¯¤æ°ç¹éå²ä¼©éå¶Ðéæ¦æªºå¨´?
        # GitHub éã¦â¬?        if big["github_user"]:
            events = fetch_github_events(big["github_user"])
            for e in events:
                e["name"] = f"{name} (@{big['github_user']})"
                e["source"] = "GitHub"
                all_results.append(e)
            print(f"  GitHub: {len(events)} é?)
            time.sleep(0.3)

        # Twitter
        if big["twitter_id"]:
            tweets = fetch_twitter_tweets(big["twitter_id"])
            for t in tweets:
                t["name"] = name
                t["source"] = "Twitter"
                all_results.append(t)
            print(f"  Twitter: {len(tweets)} é?)
            time.sleep(0.5)

        # å¯°î¼å´¥
        if big["weibo_uid"]:
            weibos = fetch_weibo_posts(big["weibo_uid"])
            for w in weibos:
                w["name"] = name
                w["source"] = "å¯°î¼å´¥"
                all_results.append(w)
            print(f"  å¯°î¼å´¥: {len(weibos)} é?)
            time.sleep(0.5)

    print(f"\né¦æ³ é¬æî¸é²å¬æ³¦ {len(all_results)} éâ³å§©é¬?)

    # ç¼æç§é»è¾¨æéå­îæ¶è½°èé?    if all_results:
        translate_batch(all_results)

    if not all_results:
        print("æµ å©æ£©éç³æéã¦â¬ä¾ç´æµ å¶å½é«ä½ºâéã¦å§¤")
        card = build_feishu_text([])
    else:
        card = build_feishu_card(all_results)

    send_to_feishu(card)
    print("=== é²å¬æ³¦ç¹å±¾å ===")


if __name__ == "__main__":
    main()
