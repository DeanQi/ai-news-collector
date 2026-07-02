# AIé¦å ãæµ£îå§©é¬ä½¹æ£©é¶?
å§£å¿ãéæ¤¾å«éå æ£¿ 9:00 é·îå§©é²å¬æ³¦ AI é¦å ãæµ£îæ®éâ¬éæ¿å§©é¬ä¾ç´éºã©â¬ä½½å¦æ¤ç°åç¼ãæºé£ã¤æ±é?
## é²å¬æ³¦é¼å¨æ´¿

çåæ´æµ ã¤ç¬ 32 æµ£?ç¼?AI é¦å ãæµ£îæ°éçç¯é?
| ç»«è¯²å | æµè¹å¢¿/ç¼å­ç² |
|------|----------|
| æ¤¤åéªæ£°åî» | Yann LeCun, Geoffrey Hinton, Yoshua Bengio, Ilya Sutskever, Sam Altman, Demis Hassabis, éåº¨î£æ¤? éå­ä»¼æ?|
| æ¾¶ÑÄé¨?| Andrej Karpathy, Dario Amodei, Aidan Gomez, Noam Shazeer, å§ä½¹æé¿?DeepSeek) |
| å¯®â¬å©§æ®æé¬?| Clement Delangue, Thomas Wolf, Lukas Biewald |
| æ¶îæµAI | å¯®ç±ç°¹é? éæ­æ¾(éé¸¿æ°¨), éå¬ªç¬å®¸?é§æ§çª), éåº¡ç´æ¾¶?éæµç«´æ¶å©å¢¿), éã©ç¼ç»?360), æ¦åªç²é?|
| çï¸½æ¹³éå¶é¨ | Percy Liang, Jim Fan, Christopher Manning, Pieter Abbeel, Sergey Levine |
| é²å¶î¦ç¼å­ç² | Meta FAIR, Google DeepMind, OpenAI, Anthropic, Cohere, HuggingFace |

## éçåµå©§?
| éçåµå©§?| çå­æ§ | éîæéâ¬çä¾îæ¾¶æ ­å¤ç¼?|
|--------|------|:---:|
| ArXiv | éâ¬éæîéå·ç´æ©?8çå¿æ¤é?| é?|
| GitHub | éîç´éã¦â¬ä¾ç´Push/Star/PR/Issueç»å¤ç´ | é?|
| Twitter | éâ¬éçå¸¹é?| éâ¬ç?Twitter API Bearer Token |
| å¯°î¼å´¥ | éâ¬éæ¿äºé?| éâ¬çä½¸äºé?Cookie |

## è¹î¦â¬ç·ç´æ¿®?
### 1. éæ¶ç¼ GitHub æµ æ³ç°±

```bash
# éå¬®æ®é´æ §åµæ¿®å¬ªå¯²æµ æ³ç°±
git init
git add .
git commit -m "init: AI news collector"
git remote add origin <æµ£çµæ®æµ æ³ç°±é¦æ¿æ½>
git push -u origin main
```

### 2. é°å¶ç Secrets

é¦?GitHub æµ æ³ç°±æ¤¤ç¸æ½°éæ­Settings` é«?`Secrets and variables` é«?`Actions` é«?`New repository secret`

| Secret éå¶Ð | çå­æ§ | è¹å­ï½ |
|-------------|------|:---:|
| `FEISHU_WEBHOOK_URL` | æ¤ç°åéåæ«æµ?Webhook é¦æ¿æ½ | é?|
| `TWITTER_BEARER_TOKEN` | Twitter API v2 Bearer Tokenéå å½²é«å¤ç´æ¶å¶å¤éæ¬ç¦æ©?Twitteré?| é?|
| `WEIBO_COOKIE` | å¯°î¼å´¥é§è¯²ç¶ Cookieéå å½²é«å¤ç´æ¶å¶å¤éæ¬ç¦æ©å§äºéæ°¾ç´ | é?|

### 3. æ¥ å²ç

éºã©â¬ä½·å¬é®ä½¸æéå­itHub Actions æµ¼æ°¬æ¹ªå§£å¿ãéæ¤¾å«éå æ£¿ 9:00 é·îå§©æ©æ¯îéåç¯éîäºéµå¬ªå§©çï¹å½é?
1. æ©æ¶åæµ æ³ç°± `Actions` æ¤¤ç¸æ½°
2. é«å¤å«¨ `Daily AI News Report`
3. éç°å® `Run workflow`

## æ¤¤å­æ´°ç¼æ´ç¯

```
.
é¹æº¾æ¢é¹â¬ .github/workflows/daily-ai-report.yml   # GitHub Actions å®¸ã¤ç¶å¨´?é¹æº¾æ¢é¹â¬ scripts/collect_ai_news.py              # é²å¬æ³¦æ¶æå¼é?é¹æº¾æ¢é¹â¬ requirements.txt                         # Python æ¸æ¿ç¦
é¹æºæ¢é¹â¬ README.md
```
*éå å´ç¹å­æ±AIé¢ç¸åéå±¼ç²æ¸æ¶å¼¬é°å¿ç´*
