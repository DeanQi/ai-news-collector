# AI圈大佬动态日报

每天北京时间 9:00 自动采集 AI 圈大佬的最新动态，推送至飞书群机器人。

## 采集范围

覆盖以下 32 位/组 AI 圈大佬和机构：

| 类别 | 人物/组织 |
|------|----------|
| 顶级领袖 | Yann LeCun, Geoffrey Hinton, Yoshua Bengio, Ilya Sutskever, Sam Altman, Demis Hassabis, 李飞飞, 吴恩达 |
| 大模型 | Andrej Karpathy, Dario Amodei, Aidan Gomez, Noam Shazeer, 梁文锋(DeepSeek) |
| 开源生态 | Clement Delangue, Thomas Wolf, Lukas Biewald |
| 中国AI | 张亚勤, 唐杰(智谱), 王小川(百川), 李开复(零一万物), 周鸿祎(360), 黄仁勋 |
| 学术前沿 | Percy Liang, Jim Fan, Christopher Manning, Pieter Abbeel, Sergey Levine |
| 重要组织 | Meta FAIR, Google DeepMind, OpenAI, Anthropic, Cohere, HuggingFace |

## 数据源

| 数据源 | 说明 | 是否需要额外配置 |
|--------|------|:---:|
| ArXiv | 最新论文（近48小时） | 否 |
| GitHub | 公开动态（Push/Star/PR/Issue等） | 否 |
| Twitter | 最新推文 | 需要 Twitter API Bearer Token |
| 微博 | 最新微博 | 需要微博 Cookie |

## 快速开始

### 1. 创建 GitHub 仓库

```bash
git init
git add .
git commit -m init: AI news collector
git remote add origin [你的仓库地址]
git push -u origin main
```

### 2. 配置 Secrets

| Secret 名称 | 说明 | 必填 |
|-------------|------|:---:|
| FEISHU_WEBHOOK_URL | 飞书机器人 Webhook 地址 | 是 |
| TWITTER_BEARER_TOKEN | Twitter API v2 Bearer Token | 否 |
| WEIBO_COOKIE | 微博登录 Cookie | 否 |

### 3. 验证

每天北京时间 9:00 自动运行。可手动触发：Actions → Daily AI News Report → Run workflow

## 项目结构

- `.github/workflows/daily-ai-report.yml` - GitHub Actions 工作流
- `scripts/collect_ai_news.py` - 采集主脚本（含翻译）
- `requirements.txt` - Python 依赖
- `README.md`
