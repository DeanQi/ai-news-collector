---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: a09faa462e364ef9c5f711b55b4ab9b6_ca7eed3e761b11f1a8895254002afed2
    ReservedCode1: YKNAzUaN5isajitRU3ApwbVLULlfRkG09fwHk8nufNAgGEVrzftUSkheNTz13w6Enq0Nug5g4rqtFQKEXQ2biSSiFCPR3l2KQM0bLw67IvEgMz6c13NlQc0BJ9K71QC1eVPRwwWzRvARwKhsWseWjvG1gHhlCC8cvDQWoyOKIa1ZFUFNi+MLageVWTg=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: a09faa462e364ef9c5f711b55b4ab9b6_ca7eed3e761b11f1a8895254002afed2
    ReservedCode2: YKNAzUaN5isajitRU3ApwbVLULlfRkG09fwHk8nufNAgGEVrzftUSkheNTz13w6Enq0Nug5g4rqtFQKEXQ2biSSiFCPR3l2KQM0bLw67IvEgMz6c13NlQc0BJ9K71QC1eVPRwwWzRvARwKhsWseWjvG1gHhlCC8cvDQWoyOKIa1ZFUFNi+MLageVWTg=
---

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
# 克隆或初始化仓库
git init
git add .
git commit -m "init: AI news collector"
git remote add origin <你的仓库地址>
git push -u origin main
```

### 2. 配置 Secrets

在 GitHub 仓库页面：`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

| Secret 名称 | 说明 | 必填 |
|-------------|------|:---:|
| `FEISHU_WEBHOOK_URL` | 飞书机器人 Webhook 地址 | ✅ |
| `TWITTER_BEARER_TOKEN` | Twitter API v2 Bearer Token（可选，不配则跳过 Twitter） | ❌ |
| `WEIBO_COOKIE` | 微博登录 Cookie（可选，不配则跳过微博） | ❌ |

### 3. 验证

推送代码后，GitHub Actions 会在每天北京时间 9:00 自动运行。也可以手动触发：

1. 进入仓库 `Actions` 页面
2. 选择 `Daily AI News Report`
3. 点击 `Run workflow`

## 项目结构

```
.
├── .github/workflows/daily-ai-report.yml   # GitHub Actions 工作流
├── scripts/collect_ai_news.py              # 采集主脚本
├── requirements.txt                         # Python 依赖
└── README.md
```
*（内容由AI生成，仅供参考）*
