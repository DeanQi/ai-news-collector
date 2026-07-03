#!/usr/bin/env python3
"""
AI鍦堝ぇ浣姩鎬佹棩鎶ラ噰闆嗚剼鏈?- 閲囬泦 ArXiv 鏈€鏂拌鏂?- 閲囬泦 GitHub 鍏紑鍔ㄦ€?- 閲囬泦 Twitter 鍔ㄦ€侊紙闇€閰嶇疆 TWITTER_BEARER_TOKEN锛?- 閲囬泦寰崥鍔ㄦ€侊紙闇€閰嶇疆 WEIBO_COOKIE锛?- 鎺ㄩ€佸埌椋炰功鏈哄櫒浜?Webhook
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

# 鈹€鈹€鈹€ 閰嶇疆 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")
WEIBO_COOKIE = os.environ.get("WEIBO_COOKIE", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

BEIJING_TZ = pytz.timezone("Asia/Shanghai")
TODAY = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
YESTERDAY = (datetime.now(BEIJING_TZ) - timedelta(days=1))
WEEK_AGO = (datetime.now(BEIJING_TZ) - timedelta(days=7))

# 姣忎釜鏁版嵁婧愭渶澶氬睍绀烘潯鏁?MAX_PER_SOURCE = 1

# 鈹€鈹€鈹€ 澶т浆淇℃伅搴?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

# 鏍煎紡: { "name": "涓枃鍚?甯哥敤鍚?, "arxiv_name": "ArXiv浣滆€呭悕(Last, First)", "github_user": "GitHub鐢ㄦ埛鍚嶆垨org", "twitter_id": "Twitter鐢ㄦ埛ID鏁板瓧", "twitter_username": "Twitter鐢ㄦ埛鍚?, "weibo_uid": "寰崥UID" }
BIG_NAMES = [
    # === 椤剁骇鐮旂┒鏈烘瀯/浼佷笟棰嗚 ===
    {"name": "Yann LeCun",           "arxiv_name": "LeCun, Yann",            "github_user": "",                   "twitter_id": "105943820",           "twitter_username": "ylecun",              "weibo_uid": ""},
    {"name": "Geoffrey Hinton",      "arxiv_name": "Hinton, Geoffrey",       "github_user": "",                   "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": ""},
    {"name": "Yoshua Bengio",        "arxiv_name": "Bengio, Yoshua",         "github_user": "",                   "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": ""},
    {"name": "Ilya Sutskever",       "arxiv_name": "Sutskever, Ilya",        "github_user": "",                   "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": ""},
    {"name": "Sam Altman",           "arxiv_name": "",                       "github_user": "",                   "twitter_id": "19497576",            "twitter_username": "sama",                "weibo_uid": ""},
    {"name": "Demis Hassabis",       "arxiv_name": "Hassabis, Demis",        "github_user": "",                   "twitter_id": "389534645",           "twitter_username": "demishassabis",       "weibo_uid": ""},
    {"name": "鏉庨椋?(Fei-Fei Li)",   "arxiv_name": "Li, Fei-Fei",            "github_user": "",                   "twitter_id": "978780836951838720",  "twitter_username": "drfeifei",             "weibo_uid": ""},
    {"name": "鍚存仼杈?(Andrew Ng)",    "arxiv_name": "Ng, Andrew",             "github_user": "andrewng",           "twitter_id": "823533",              "twitter_username": "AndrewYNg",            "weibo_uid": ""},

    # === 澶фā鍨?LLM鏂瑰悜 ===
    {"name": "Andrej Karpathy",      "arxiv_name": "Karpathy, Andrej",       "github_user": "karpathy",           "twitter_id": "16539359",            "twitter_username": "karpathy",             "weibo_uid": ""},
    {"name": "Dario Amodei",         "arxiv_name": "Amodei, Dario",          "github_user": "",                   "twitter_id": "16668453",            "twitter_username": "DarioAmodei",          "weibo_uid": ""},
    {"name": "Aidan Gomez",          "arxiv_name": "Gomez, Aidan",           "github_user": "",                   "twitter_id": "2347577145",          "twitter_username": "aidan_mclau",          "weibo_uid": ""},
    {"name": "Noam Shazeer",         "arxiv_name": "Shazeer, Noam",          "github_user": "",                   "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": ""},
    {"name": "姊佹枃閿?(DeepSeek)",     "arxiv_name": "",                       "github_user": "deepseek-ai",        "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": ""},

    # === 寮€婧?宸ュ叿鐢熸€?===
    {"name": "Clement Delangue",     "arxiv_name": "",                       "github_user": "ClementDelangue",    "twitter_id": "13260032",            "twitter_username": "ClementDelangue",      "weibo_uid": ""},
    {"name": "Thomas Wolf",          "arxiv_name": "",                       "github_user": "thomwolf",           "twitter_id": "14345915",            "twitter_username": "Thom_Wolf",            "weibo_uid": ""},
    {"name": "Lukas Biewald",        "arxiv_name": "",                       "github_user": "lukas",              "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": ""},

    # === 涓浗AI鍦?===
    {"name": "寮犱簹鍕?,               "arxiv_name": "Zhang, Ya-Qin",           "github_user": "",                   "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": "1645171780"},
    {"name": "鍞愭澃 (鏅鸿氨/ChatGLM)",   "arxiv_name": "Tang, Jie",              "github_user": "THUDM",              "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": ""},
    {"name": "鐜嬪皬宸?(鐧惧窛鏅鸿兘)",     "arxiv_name": "",                       "github_user": "baichuan-inc",       "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": "1582488432"},
    {"name": "鏉庡紑澶?(闆朵竴涓囩墿)",     "arxiv_name": "Lee, Kai-Fu",            "github_user": "",                   "twitter_id": "21443430",            "twitter_username": "kaifulee",             "weibo_uid": "1197161814"},
    {"name": "鍛ㄩ缚绁?(360)",         "arxiv_name": "",                       "github_user": "",                   "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": "1708942053"},
    {"name": "榛勪粊鍕?(Jensen Huang)", "arxiv_name": "",                       "github_user": "",                   "twitter_id": "",                     "twitter_username": "",                    "weibo_uid": ""},

    # === 瀛︽湳鍓嶆部 ===
    {"name": "Percy Liang",          "arxiv_name": "Liang, Percy",           "github_user": "",                   "twitter_id": "26749844",            "twitter_username": "percyliang",           "weibo_uid": ""},
    {"name": "Jim Fan",              "arxiv_name": "Fan, Jim",               "github_user": "",                   "twitter_id": "1203899672",          "twitter_username": "DrJimFan",             "weibo_uid": ""},
    {"name": "Christopher Manning",  "arxiv_name": "Manning, Christopher",   "github_user": "",                   "twitter_id": "46721826",            "twitter_username": "chrmanning",           "weibo_uid": ""},
    {"name": "Pieter Abbeel",        "arxiv_name": "Abbeel, Pieter",         "github_user": "",                   "twitter_id": "105943362",           "twitter_username": "pabbeel",              "weibo_uid": ""},
    {"name": "Sergey Levine",        "arxiv_name": "Levine, Sergey",         "github_user": "",                   "twitter_id": "3352472124",          "twitter_username": "svlevine",             "weibo_uid": ""},

    # === 閲嶈缁勭粐/鍥㈤槦 ===
    {"name": "Meta FAIR",            "arxiv_name": "",                       "github_user": "facebookresearch",   "twitter_id": "14825531",            "twitter_username": "MetaAI",               "weibo_uid": ""},
    {"name": "Google DeepMind",      "arxiv_name": "",                       "github_user": "google-deepmind",    "twitter_id": "1317668457",          "twitter_username": "GoogleDeepMind",       "weibo_uid": ""},
    {"name": "OpenAI",               "arxiv_name": "",                       "github_user": "openai",             "twitter_id": "4398626122",          "twitter_username": "OpenAI",               "weibo_uid": ""},
    {"name": "Anthropic",            "arxiv_name": "",                       "github_user": "anthropics",         "twitter_id": "1405248728",          "twitter_username": "AnthropicAI",          "weibo_uid": ""},
    {"name": "Cohere",               "arxiv_name": "",                       "github_user": "cohere-ai",          "twitter_id": "1240398540438073344", "twitter_username": "cohere",               "weibo_uid": ""},
    {"name": "HuggingFace",          "arxiv_name": "",                       "github_user": "huggingface",        "twitter_id": "1078992647933444096", "twitter_username": "huggingface",          "weibo_uid": ""},
]


# 鈹€鈹€鈹€ ArXiv 璁烘枃閲囬泦 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def fetch_arxiv_papers(arxiv_name, max_results=MAX_PER_SOURCE):
    """鏌ヨ鏌愪綔鑰呰繎 48 灏忔椂鍐呯殑 ArXiv 鏂拌鏂?""
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
        print(f"  [ArXiv] {arxiv_name} 璇锋眰澶辫触: {e}")
        return []

    feed = feedparser.parse(resp.text)
    papers = []
    cutoff = WEEK_AGO.replace(tzinfo=None)  # feedparser 鐨?published_parsed 鏄?naive UTC

    for entry in feed.entries:
        published = entry.get("published_parsed")
        if published is None:
            # 灏濊瘯浠?arxiv:published 鎴?updated 鑾峰彇
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

        # 鎻愬彇 arxiv ID
        arxiv_id = entry.get("id", "").split("/abs/")[-1]
        arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
        title = entry.get("title", "Unknown").strip().replace("\n", " ")
        # 娓呯悊鏍囬涓浣欑殑绌虹櫧
        title = " ".join(title.split())

        papers.append({
            "title": title,
            "url": arxiv_url,
            "date": pub_dt.strftime("%Y-%m-%d"),
        })

    return papers


# 鈹€鈹€鈹€ GitHub 鍔ㄦ€侀噰闆?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def fetch_github_events(github_user, max_results=MAX_PER_SOURCE):
    """鏌ヨ GitHub 鐢ㄦ埛/缁勭粐杩?7 澶╁叕寮€鍔ㄦ€?""
    if not github_user:
        return []

    headers = {"Accept": "application/vnd.github+json", "User-Agent": "AI-News-Collector/1.0"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    # 鍒ゆ柇鏄敤鎴疯繕鏄粍缁囷細鍏堝皾璇?users endpoint
    url = f"https://api.github.com/users/{github_user}/events/public?per_page=20"

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 404:
            # 鍙兘鏄粍缁囷紝鐢?orgs endpoint
            url = f"https://api.github.com/orgs/{github_user}/events?per_page=20"
            resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [GitHub] {github_user} 璇锋眰澶辫触: {e}")
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
    """鏍煎紡鍖?GitHub Event 涓虹畝鐭弿杩?""
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


# 鈹€鈹€鈹€ Twitter 鍔ㄦ€侀噰闆嗭紙闇€ TWITTER_BEARER_TOKEN锛夆攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def fetch_twitter_rss(twitter_username, max_results=MAX_PER_SOURCE):
    """閫氳繃 Nitter RSS 鑾峰彇鎺ㄦ枃锛圱witter API 涓嶅彲鐢ㄦ椂鐨勯檷绾ф柟妗堬級"""
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
            print(f"  [Nitter RSS] {rss_url} 璇锋眰澶辫触: {e}")
            continue

        try:
            root = ET.fromstring(resp.text)
        except ET.ParseError as e:
            print(f"  [Nitter RSS] XML 瑙ｆ瀽澶辫触: {e}")
            continue

        # RSS 2.0 鏍煎紡: channel -> item
        for item in root.iter("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            pub_date_el = item.find("pubDate")

            title = title_el.text if title_el is not None else ""
            link = link_el.text if link_el is not None else ""
            pub_date_str = pub_date_el.text if pub_date_el is not None else ""

            if not title or not link:
                continue

            # 瑙ｆ瀽 pubDate锛圧FC 2822 鏍煎紡: "Thu, 03 Jul 2026 12:00:00 GMT"锛?            try:
                pub_dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
                pub_dt = pub_dt.replace(tzinfo=timezone.utc)
            except Exception:
                # 灏濊瘯涓嶅甫鏄熸湡鐨勬牸寮?                try:
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

        # 鎴愬姛鑾峰彇鍒版暟鎹氨璺冲嚭
        if results:
            break

    return results[:max_results]


def fetch_twitter_tweets(twitter_id, twitter_username="", max_results=MAX_PER_SOURCE):
    """鏌ヨ Twitter 鐢ㄦ埛鏈€杩戞帹鏂囷紙闇€ bearer token锛夛紝API 涓嶅彲鐢ㄦ椂鑷姩闄嶇骇鍒?Nitter RSS"""
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
            print(f"  Twitter API 涓嶅彲鐢?鐘舵€佺爜:{resp.status_code})锛岄檷绾у埌 Nitter RSS for @{twitter_username}")
            return fetch_twitter_rss(twitter_username, max_results)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status_code = resp.status_code if resp is not None else 0
        # 妫€鏌ユ槸鍚﹀凡缁忚涓婇潰鐨?if 鎹曟崏杩囷紙鐞嗚涓婁笉浼氳蛋鍒拌繖閲岋紝浣嗕繚鐣欏厹搴曪級
        if status_code in (402, 403, 429):
            print(f"  Twitter API 涓嶅彲鐢?鐘舵€佺爜:{status_code})锛岄檷绾у埌 Nitter RSS for @{twitter_username}")
            return fetch_twitter_rss(twitter_username, max_results)
        raise
    except Exception as e:
        print(f"  [Twitter] {twitter_id} 璇锋眰澶辫触: {e}")
        if twitter_username:
            print(f"  闄嶇骇鍒?Nitter RSS for @{twitter_username}")
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


# 鈹€鈹€鈹€ 寰崥鍔ㄦ€侀噰闆嗭紙闇€ WEIBO_COOKIE锛夆攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def fetch_weibo_posts(weibo_uid, max_results=MAX_PER_SOURCE):
    """鏌ヨ寰崥鐢ㄦ埛鏈€杩戝姩鎬侊紙闇€ cookie锛?""
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
        print(f"  [Weibo] {weibo_uid} 璇锋眰澶辫触: {e}")
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
            # 寰崥鏃堕棿鏍煎紡 "Thu Jul 02 09:00:00 +0800 2026"
            created = datetime.strptime(created_str, "%a %b %d %H:%M:%S %z %Y")
        except Exception:
            continue
        if created < cutoff:
            continue

        post_id = post.get("id", "") or post.get("mid", "")
        post_url = f"https://weibo.com/{weibo_uid}/{post_id}" if post_id else ""
        # 鎻愬彇绾枃鏈?        text_raw = post.get("text_raw", "") or post.get("text", "")
        # 鍘绘帀 HTML 鏍囩
        import re
        text = re.sub(r"<[^>]+>", "", text_raw)[:120].strip()

        results.append({
            "description": text,
            "url": post_url,
            "date": created.strftime("%Y-%m-%d %H:%M"),
        })

    return results[:max_results]


# 鈹€鈹€鈹€ 缈昏瘧 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def contains_chinese(text):
    """鍒ゆ柇鏂囨湰鏄惁鍖呭惈涓枃"""
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def translate_batch(items, max_retries=2):
    """鎵归噺缈昏瘧 items 涓殑 description 瀛楁锛堜粎缈昏瘧涓嶅惈涓枃鐨勶級"""
    from deep_translator import GoogleTranslator

    to_translate = []
    indices = []
    for i, item in enumerate(items):
        desc = item.get("description", "")
        if desc and not contains_chinese(desc):
            to_translate.append(desc)
            indices.append(i)

    if not to_translate:
        print("  鎵€鏈夊唴瀹瑰凡涓轰腑鏂囷紝璺宠繃缈昏瘧")
        return

    print(f"  寰呯炕璇?{len(to_translate)} 鏉¤嫳鏂囧唴瀹?..")
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
                    print(f"  缈昏瘧澶辫触: {text[:40]}... 鈫?{e}")
                    results.append(text)  # 澶辫触淇濈暀鍘熸枃

    for idx, translated in zip(indices, results):
        items[idx]["translated"] = translated

    print(f"  缈昏瘧瀹屾垚 {len(results)} 鏉?)


# 鈹€鈹€鈹€ 椋炰功鎺ㄩ€?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def build_feishu_card(all_results):
    """鏋勫缓椋炰功鍗＄墖娑堟伅"""
    header_text = f"AI鍦堝ぇ浣姩鎬佹棩鎶?| {TODAY}"
    elements = []

    # 缁熻鎬绘暟
    total_papers = sum(1 for r in all_results if r["source"] == "ArXiv")
    total_github = sum(1 for r in all_results if r["source"] == "GitHub")
    total_twitter = sum(1 for r in all_results if r["source"] == "Twitter")
    total_weibo = sum(1 for r in all_results if r["source"] == "寰崥")

    # 鎽樿琛?    summary_parts = []
    if total_papers:
        summary_parts.append(f"馃搫 璁烘枃 {total_papers} 绡?)
    if total_github:
        summary_parts.append(f"馃捇 GitHub {total_github} 鏉?)
    if total_twitter:
        summary_parts.append(f"馃惁 Twitter {total_twitter} 鏉?)
    if total_weibo:
        summary_parts.append(f"馃寪 寰崥 {total_weibo} 鏉?)

    summary = " | ".join(summary_parts) if summary_parts else "浠婃棩鏆傛棤鏂板姩鎬?

    elements.append({
        "tag": "div",
        "text": {"tag": "lark_md", "content": f"**{summary}**\n"},
    })

    # 鎸夋潵婧愬垎缁?    source_groups = [
        ("馃搫 ArXiv 鏈€鏂拌鏂?, "ArXiv"),
        ("馃捇 GitHub 鍔ㄦ€?, "GitHub"),
        ("馃惁 Twitter 鍔ㄦ€?, "Twitter"),
        ("馃寪 寰崥鍔ㄦ€?, "寰崥"),
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
        # 椋炰功鍗＄墖鍗曞厓绱犳湁鍐呭闀垮害闄愬埗锛岃繃闀垮垯鎷嗗垎
        if len(content) > 4000:
            # 鎴柇澶勭悊锛屾瘡鏉″崟鐙彂閫佺殑鏂瑰紡杩囦簬澶嶆潅锛岃繖閲屽彇鍓嶈嫢骞叉潯
            content = content[:3800] + "\n... (鍐呭杩囬暱宸叉埅鏂?"

        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": content},
        })
        elements.append({"tag": "hr"})

    # 绉婚櫎鏈€鍚庝竴涓浣欑殑 hr
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

    # 浼扮畻鍗＄墖澶у皬锛岄涔﹂檺鍒剁害 30KB
    card_json = json.dumps(card, ensure_ascii=False)
    if len(card_json) > 25000:
        # 闄嶇骇涓虹畝鍗曟枃鏈秷鎭?        return build_feishu_text(all_results)

    return card


def build_feishu_text(all_results):
    """闄嶇骇锛氫娇鐢ㄥ瘜鏂囨湰娑堟伅"""
    lines = [f"AI鍦堝ぇ浣姩鎬佹棩鎶?| {TODAY}", ""]

    source_groups = [
        ("馃搫 ArXiv 鏈€鏂拌鏂?, "ArXiv"),
        ("馃捇 GitHub 鍔ㄦ€?, "GitHub"),
        ("馃惁 Twitter 鍔ㄦ€?, "Twitter"),
        ("馃寪 寰崥鍔ㄦ€?, "寰崥"),
    ]

    for group_title, source in source_groups:
        group_items = [r for r in all_results if r["source"] == source]
        if not group_items:
            continue

        lines.append(group_title)
        for item in group_items[:MAX_PER_SOURCE * 3]:  # 闄愬埗鏉℃暟
            desc = item.get("translated") or item["description"]
            lines.append(
                f"  鈥?{item['name']}: {desc[:100]}"
            )
        lines.append("")

    if not any(r for r in all_results):
        lines.append("浠婃棩鏆傛棤鏂板姩鎬?)

    return {
        "msg_type": "text",
        "content": {"text": "\n".join(lines)},
    }


def send_to_feishu(card):
    """鍙戦€佹秷鎭埌椋炰功 webhook"""
    if not FEISHU_WEBHOOK_URL:
        print("鉂?鏈厤缃?FEISHU_WEBHOOK_URL锛岃烦杩囨帹閫?)
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
            print("鉁?椋炰功鎺ㄩ€佹垚鍔?)
            return True
        else:
            print(f"鉂?椋炰功鎺ㄩ€佸け璐? {result}")
            return False
    except Exception as e:
        print(f"鉂?椋炰功鎺ㄩ€佸紓甯? {e}")
        return False


# 鈹€鈹€鈹€ 涓绘祦绋?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def main():
    print(f"=== AI鍦堝ぇ浣姩鎬侀噰闆嗗紑濮?({TODAY}) ===")

    all_results = []

    for big in BIG_NAMES:
        name = big["name"]
        print(f"\n馃攳 閲囬泦: {name}")

        # ArXiv 璁烘枃
        if big["arxiv_name"]:
            papers = fetch_arxiv_papers(big["arxiv_name"])
            for p in papers:
                p["name"] = name
                p["source"] = "ArXiv"
                all_results.append(p)
            print(f"  ArXiv: {len(papers)} 绡?)
            time.sleep(1)  # 绀艰矊寤惰繜锛岄伩鍏嶈Е鍙戦檺娴?
        # GitHub 鍔ㄦ€?        if big["github_user"]:
            events = fetch_github_events(big["github_user"])
            for e in events:
                e["name"] = f"{name} (@{big['github_user']})"
                e["source"] = "GitHub"
                all_results.append(e)
            print(f"  GitHub: {len(events)} 鏉?)
            time.sleep(0.3)

        # Twitter
        if big["twitter_id"]:
            tweets = fetch_twitter_tweets(big["twitter_id"], big.get("twitter_username", ""))
            for t in tweets:
                t["name"] = name
                t["source"] = "Twitter"
                all_results.append(t)
            print(f"  Twitter: {len(tweets)} 鏉?)
            time.sleep(0.5)

        # 寰崥
        if big["weibo_uid"]:
            weibos = fetch_weibo_posts(big["weibo_uid"])
            for w in weibos:
                w["name"] = name
                w["source"] = "寰崥"
                all_results.append(w)
            print(f"  寰崥: {len(weibos)} 鏉?)
            time.sleep(0.5)

    print(f"\n馃搳 鎬昏閲囬泦 {len(all_results)} 鏉″姩鎬?)

    # 缈昏瘧鑻辨枃鍐呭涓轰腑鏂?    if all_results:
        translate_batch(all_results)

    if not all_results:
        print("浠婃棩鏃犳柊鍔ㄦ€侊紝浠嶅彂閫佺┖鏃ユ姤")
        card = build_feishu_text([])
    else:
        card = build_feishu_card(all_results)

    send_to_feishu(card)
    print("=== 閲囬泦瀹屾垚 ===")


if __name__ == "__main__":
    main()
