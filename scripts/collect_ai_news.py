#!/usr/bin/env python3
import os, sys, json, time, hashlib, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import requests, feedparser, pytz

FEISHU_WEBHOOK_URL = os.environ.get(FEISHU_WEBHOOK_URL, ")
TWITTER_BEARER_TOKEN = os.environ.get(TWITTER_BEARER_TOKEN, ")
WEIBO_COOKIE = os.environ.get(WEIBO_COOKIE, ")
BEIJING_TZ = pytz.timezone(Asia/Shanghai)
TODAY = datetime.now(BEIJING_TZ).strftime(%Y-%m-%d)
YESTERDAY = datetime.now(BEIJING_TZ) - timedelta(days=1)
MAX_PER_SOURCE = 1

BIG_NAMES = [
    {name: Yann LeCun, arxiv_name: LeCun, Yann, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Geoffrey Hinton, arxiv_name: Hinton, Geoffrey, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Yoshua Bengio, arxiv_name: Bengio, Yoshua, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Ilya Sutskever, arxiv_name: Sutskever, Ilya, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Sam Altman, arxiv_name: ", github_user: ", twitter_id: ", weibo_uid: "},
    {name: Demis Hassabis, arxiv_name: Hassabis, Demis, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Li Fei-Fei, arxiv_name: Li, Fei-Fei, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Andrew Ng, arxiv_name: Ng, Andrew, github_user: andrewng, twitter_id: ", weibo_uid: "},
    {name: Andrej Karpathy, arxiv_name: Karpathy, Andrej, github_user: karpathy, twitter_id: ", weibo_uid: "},
    {name: Dario Amodei, arxiv_name: Amodei, Dario, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Aidan Gomez, arxiv_name: Gomez, Aidan, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Noam Shazeer, arxiv_name: Shazeer, Noam, github_user: ", twitter_id: ", weibo_uid: "},
    {name: DeepSeek, arxiv_name: ", github_user: deepseek-ai, twitter_id: ", weibo_uid: "},
    {name: Clement Delangue, arxiv_name: ", github_user: ClementDelangue, twitter_id: ", weibo_uid: "},
    {name: Thomas Wolf, arxiv_name: ", github_user: thomwolf, twitter_id: ", weibo_uid: "},
    {name: Lukas Biewald, arxiv_name: ", github_user: lukas, twitter_id: ", weibo_uid: "},
    {name: Zhang Ya-Qin, arxiv_name: Zhang, Ya-Qin, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Tang Jie (Zhipu), arxiv_name: Tang, Jie, github_user: THUDM, twitter_id: ", weibo_uid: "},
    {name: Wang Xiaochuan (Baichuan), arxiv_name: ", github_user: baichuan-inc, twitter_id: ", weibo_uid: "},
    {name: Kai-Fu Lee, arxiv_name: Lee, Kai-Fu, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Zhou Hongyi (360), arxiv_name: ", github_user: ", twitter_id: ", weibo_uid: "},
    {name: Jensen Huang, arxiv_name: ", github_user: ", twitter_id: ", weibo_uid: "},
    {name: Percy Liang, arxiv_name: Liang, Percy, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Jim Fan, arxiv_name: Fan, Jim, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Christopher Manning, arxiv_name: Manning, Christopher, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Pieter Abbeel, arxiv_name: Abbeel, Pieter, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Sergey Levine, arxiv_name: Levine, Sergey, github_user: ", twitter_id: ", weibo_uid: "},
    {name: Meta FAIR, arxiv_name: ", github_user: facebookresearch, twitter_id: ", weibo_uid: "},
    {name: Google DeepMind, arxiv_name: ", github_user: google-deepmind, twitter_id: ", weibo_uid: "},
    {name: OpenAI, arxiv_name: ", github_user: openai, twitter_id: ", weibo_uid: "},
    {name: Anthropic, arxiv_name: ", github_user: anthropics, twitter_id: ", weibo_uid: "},
    {name: Cohere, arxiv_name: ", github_user: cohere-ai, twitter_id: ", weibo_uid: "},
    {name: HuggingFace, arxiv_name: ", github_user: huggingface, twitter_id: ", weibo_uid: "},
]
def fetch_arxiv_papers(arxiv_name, max_results=MAX_PER_SOURCE):
    if not arxiv_name:
        return []
    url = (fhttp://export.arxiv.org/api/query
           f?search_query=au:{requests.utils.quote(arxiv_name)}
           f&sortBy=submittedDate&sortOrder=descending&max_results={max_results})
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f [ArXiv] {arxiv_name} query failed: {e})
        return []
    feed = feedparser.parse(resp.text)
    papers = []
    cutoff = YESTERDAY.replace(tzinfo=None)
    for entry in feed.entries:
        published = entry.get(published_parsed)
        if published is None:
            if hasattr(entry, arxiv_published):
                try:
                    published = time.strptime(entry.arxiv_published, %Y-%m-%dT%H:%M:%SZ)
                except Exception:
                    continue
            else:
                continue
        pub_dt = datetime(*published[:6])
        if pub_dt < cutoff:
            continue
        arxiv_id = entry.get(id, ").split(/abs/)[-1]
        arxiv_url = fhttps://arxiv.org/abs/{arxiv_id}
        title = entry.get(title, Unknown).strip().replace(\n,  )
        title =  .join(title.split())
        papers.append({title: title, url: arxiv_url, date: pub_dt.strftime(%Y-%m-%d)})
    return papers


def _format_github_event(ev):
    ev_type = ev.get(type, ")
    repo = ev.get(repo, {}).get(name, ")
    payload = ev.get(payload, {})
    if ev_type == PushEvent:
        commits = payload.get(commits, [])
        n = len(commits)
        if n == 0:
            return None
        msg = commits[0].get(message, ").split(\n)[0][:60]
        if n == 1:
            return fPush to {repo}: {msg}
        return fPush {n} commits to {repo}: {msg}
    elif ev_type == CreateEvent:
        ref_type = payload.get(ref_type, branch)
        ref = payload.get(ref, ")
        return fCreated {ref_type} {ref} in {repo}
    elif ev_type == DeleteEvent:
        ref_type = payload.get(ref_type, branch)
        ref = payload.get(ref, ")
        return fDeleted {ref_type} {ref} in {repo}
    elif ev_type == WatchEvent:
        return fStarred {repo}
    elif ev_type == ForkEvent:
        return fForked {repo}
    elif ev_type == IssuesEvent:
        action = payload.get(action, ")
        issue = payload.get(issue, {}).get(title, ")[:60]
        return f{action.capitalize()} issue in {repo}: {issue}
    elif ev_type == IssueCommentEvent:
        issue = payload.get(issue, {}).get(title, ")[:60]
        return fCommented on issue in {repo}: {issue}
    elif ev_type == PullRequestEvent:
        action = payload.get(action, ")
        pr = payload.get(pull_request, {}).get(title, ")[:60]
        return f{action.capitalize()} PR in {repo}: {pr}
    elif ev_type == ReleaseEvent:
        release = payload.get(release, {}).get(name, ")
        return fReleased {release} in {repo}
    elif ev_type == PublicEvent:
        return fMade {repo} public
    else:
        return f{ev_type} on {repo}


def fetch_github_events(github_user, max_results=MAX_PER_SOURCE):
    if not github_user:
        return []
    url = fhttps://api.github.com/users/{github_user}/events/public?per_page={max_results * 3}
    headers = {Accept: application/vnd.github+json, User-Agent: AI-News-Collector/1.0}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 404:
            url = fhttps://api.github.com/orgs/{github_user}/events?per_page={max_results * 3}
            resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f [GitHub] {github_user} query failed: {e})
        return []
    events = resp.json()
    if not isinstance(events, list):
        return []
    results = []
    cutoff = YESTERDAY.replace(tzinfo=timezone.utc)
    seen = set()
    for ev in events:
        created_str = ev.get(created_at, ")
        if not created_str:
            continue
        try:
            created = datetime.fromisoformat(created_str.replace(Z, +00:00))
        except Exception:
            continue
        if created < cutoff:
            continue
        desc = _format_github_event(ev)
        if not desc:
            continue
        repo_name = ev.get(repo, {}).get(name, ")
        event_url = fhttps://github.com/{repo_name}
        dedup_key = f{desc}|{event_url}
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        results.append({description: desc, url: event_url, date: created.strftime(%Y-%m-%d %H:%M)})
        if len(results) >= max_results:
            break
    return results
def fetch_twitter_tweets(twitter_id, max_results=MAX_PER_SOURCE):
    if not twitter_id or not TWITTER_BEARER_TOKEN:
        return []
    url = fhttps://api.twitter.com/2/users/{twitter_id}/tweets
    headers = {Authorization: fBearer {TWITTER_BEARER_TOKEN}}
    params = {max_results: max_results, tweet.fields: created_at, exclude: retweets,replies}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f [Twitter] {twitter_id} query failed: {e})
        return []
    data = resp.json()
    tweets = data.get(data, [])
    results = []
    cutoff = YESTERDAY.replace(tzinfo=timezone.utc)
    for tw in tweets:
        created_str = tw.get(created_at, ")
        try:
            created = datetime.fromisoformat(created_str.replace(Z, +00:00))
        except Exception:
            continue
        if created < cutoff:
            continue
        tw_id = tw.get(id, ")
        tw_url = fhttps://twitter.com/i/status/{tw_id}
        text = tw.get(text, ")[:120].replace(\n,  )
        results.append({description: text, url: tw_url, date: created.strftime(%Y-%m-%d %H:%M)})
    return results[:max_results]


def fetch_weibo_posts(weibo_uid, max_results=MAX_PER_SOURCE):
    if not weibo_uid or not WEIBO_COOKIE:
        return []
    url = fhttps://weibo.com/ajax/statuses/mymblog?uid={weibo_uid}&page=1&feature=0
    headers = {User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36,
               Cookie: WEIBO_COOKIE, Referer: https://weibo.com/}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f [Weibo] {weibo_uid} query failed: {e})
        return []
    try:
        data = resp.json()
    except Exception:
        return []
    posts = data.get(data, {}).get(list, [])
    results = []
    cutoff = YESTERDAY
    for post in posts:
        created_str = post.get(created_at, ")
        try:
            created = datetime.strptime(created_str, %a %b %d %H:%M:%S %z %Y)
        except Exception:
            continue
        if created < cutoff:
            continue
        post_id = post.get(id, ") or post.get(mid, ")
        post_url = fhttps://weibo.com/{weibo_uid}/{post_id} if post_id else "
        text_raw = post.get(text_raw, ") or post.get(text, ")
        import re
        text = re.sub(r<[^>]+>, ", text_raw)[:120].strip()
        results.append({description: text, url: post_url, date: created.strftime(%Y-%m-%d %H:%M)})
    return results[:max_results]
def contains_chinese(text):
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def translate_batch(items, max_retries=2):
    from deep_translator import GoogleTranslator
    to_translate = []
    indices = []
    for i, item in enumerate(items):
        desc = item.get(description, ")
        if desc and not contains_chinese(desc):
            to_translate.append(desc)
            indices.append(i)
    if not to_translate:
        print( No English content to translate)
        return
    print(f Translating {len(to_translate)} items...)
    results = []
    for text in to_translate:
        for attempt in range(max_retries):
            try:
                translated = GoogleTranslator(source=auto, target=zh-CN).translate(text)
                results.append(translated)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print(f Translation failed: {text[:40]}... err: {e})
                    results.append(text)
    for idx, translated in zip(indices, results):
        items[idx][translated] = translated
    print(f Translation done: {len(results)} items)


def build_feishu_card(all_results):
    header_text = fAI Daily Report | {TODAY}
    elements = []
    total_papers = sum(1 for r in all_results if r[source] == ArXiv)
    total_github = sum(1 for r in all_results if r[source] == GitHub)
    total_twitter = sum(1 for r in all_results if r[source] == Twitter)
    total_weibo = sum(1 for r in all_results if r[source] == Weibo)
    summary_parts = []
    if total_papers:
        summary_parts.append(fPapers {total_papers})
    if total_github:
        summary_parts.append(fGitHub {total_github})
    if total_twitter:
        summary_parts.append(fTwitter {total_twitter})
    if total_weibo:
        summary_parts.append(fWeibo {total_weibo})
    summary =  | .join(summary_parts) if summary_parts else No updates today
    elements.append({tag: div, text: {tag: lark_md, content: f**{summary}**\n}})
    source_groups = [
        (ArXiv Papers, ArXiv),
        (GitHub Activity, GitHub),
        (Twitter Posts, Twitter),
        (Weibo Posts, Weibo),
    ]
    for group_title, source in source_groups:
        group_items = [r for r in all_results if r[source] == source]
        if not group_items:
            continue
        lines = [f**{group_title}**\n]
        for item in group_items:
            name = item[name]
            desc = item.get(translated) or item[description]
            desc = desc.replace(**, ").replace(*, ")
            url = item[url]
            date = item.get(date, ")
            lines.append(f- **{name}**: [{desc}]({url}) _{date}_)
        content = \n.join(lines)
        if len(content) > 4000:
            content = content[:3800] + \n... (truncated)
        elements.append({tag: div, text: {tag: lark_md, content: content}})
        elements.append({tag: hr})
    if elements and elements[-1].get(tag) == hr:
        elements.pop()
    card = {msg_type: interactive, card: {header: {title: {tag: plain_text, content: header_text}, template: blue}, elements: elements}}
    card_json = json.dumps(card, ensure_ascii=False)
    if len(card_json) > 25000:
        return build_feishu_text(all_results)
    return card
def build_feishu_text(all_results):
    lines = [fAI Daily Report | {TODAY}, "]
    source_groups = [
        (ArXiv Papers, ArXiv),
        (GitHub Activity, GitHub),
        (Twitter Posts, Twitter),
        (Weibo Posts, Weibo),
    ]
    for group_title, source in source_groups:
        group_items = [r for r in all_results if r[source] == source]
        if not group_items:
            continue
        lines.append(group_title)
        for item in group_items[:MAX_PER_SOURCE * 3]:
            desc = item.get(translated) or item[description]
            lines.append(f - {item['name']}: {desc[:100]})
        lines.append(")
    if not any(r for r in all_results):
        lines.append(No updates today)
    return {msg_type: text, text: {content: \n.join(lines)}}


def send_to_feishu(card):
    if not FEISHU_WEBHOOK_URL:
        print([Skip] FEISHU_WEBHOOK_URL not set)
        return False
    try:
        resp = requests.post(FEISHU_WEBHOOK_URL, json=card,
                             headers={Content-Type: application/json}, timeout=15)
        resp.raise_for_status()
        result = resp.json()
        if result.get(code) == 0:
            print([OK] Feishu message sent successfully)
            return True
        else:
            print(f[Fail] Feishu returned: {result})
            return False
    except Exception as e:
        print(f[Fail] Feishu send error: {e})
        return False


def main():
    print(f=== AI News Collector Start ({TODAY}) ===)
    all_results = []
    for big in BIG_NAMES:
        name = big[name]
        print(f\nCollecting: {name})
        if big[arxiv_name]:
            papers = fetch_arxiv_papers(big[arxiv_name])
            for p in papers:
                p[name] = name
                p[source] = ArXiv
                all_results.append(p)
            print(f ArXiv: {len(papers)} papers)
            time.sleep(1)
        if big[github_user]:
            events = fetch_github_events(big[github_user])
            for e in events:
                e[name] = f{name} (@{big['github_user']})
                e[source] = GitHub
                all_results.append(e)
            print(f GitHub: {len(events)} events)
            time.sleep(0.3)
        if big[twitter_id]:
            tweets = fetch_twitter_tweets(big[twitter_id])
            for t in tweets:
                t[name] = name
                t[source] = Twitter
                all_results.append(t)
            print(f Twitter: {len(tweets)} tweets)
            time.sleep(0.5)
        if big[weibo_uid]:
            weibos = fetch_weibo_posts(big[weibo_uid])
            for w in weibos:
                w[name] = name
                w[source] = Weibo
                all_results.append(w)
            print(f Weibo: {len(weibos)} posts)
            time.sleep(0.5)
    print(f\nTotal collected: {len(all_results)} items)
    if all_results:
        translate_batch(all_results)
    if not all_results:
        print(No new updates today, sending empty report)
        card = build_feishu_text([])
    else:
        card = build_feishu_card(all_results)
    send_to_feishu(card)
    print(=== Collection Complete ===)


if __name__ == __main__:
    main()
