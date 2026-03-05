# 參與貢獻 Intel Swarm

Intel Swarm 設計為完全可擴展的系統。你可以新增研究領域、精煉現有的研究員提示詞，以及調整綜合/首席分析師的邏輯——大多數自訂不需要修改程式碼。

---

## 🌐 新增研究領域

### 第一步 — 建立研究員資料夾

```bash
mkdir -p researchers/{你的領域}/{findings,memory}
echo "# 你的領域 — 活躍議題" > researchers/{你的領域}/memory/threads.md
echo "# 你的領域 — 來源" > researchers/{你的領域}/memory/sources.md
```

### 第二步 — 加入網頁伺服器

開啟 `web/server.py`，將你的領域加入 `RESEARCHERS` 列表：

```python
RESEARCHERS = [
    ...
    {"id": "你的領域", "emoji": "🔍", "name": "Your Domain", "zh": "你的領域", "colors": "#1a1a2e,#e94560"},
    ...
]
```

**顏色建議：** 使用兩個十六進制顏色（暗色 → 強調色）作為卡片漸層。選擇與現有領域視覺上有所區別的配色。

### 第三步 — 建立研究員排程任務

```bash
openclaw cron add \
  --name "intel-你的領域" \
  --description "你的領域研究員 - 每日情報..." \
  --cron "X 6 * * *" \
  --tz "Asia/Hong_Kong" \
  --session "isolated" \
  --model "anthropic/claude-sonnet-4-6" \
  --message "$(cat researchers/你的領域/INSTRUCTIONS.md)" \
  --timeout-seconds 120 \
  --no-deliver
```

錯開分鐘偏移（選擇 0–59 之間未使用的分鐘），避免所有排程同時執行。

### 第四步 — 撰寫研究員提示詞

建立 `researchers/{你的領域}/INSTRUCTIONS.md`：

```markdown
INTERNAL_TASK - INTEL RESEARCH AGENT

你是一個私人情報研究團隊的{你的領域}研究員。

你的研究重點：[詳細描述要追蹤的信號——要具體]

## 步驟
1. 執行以下網路搜尋：
   - [查詢 1]
   - [查詢 2]
   - [查詢 3]
   - [查詢 4]
   - [查詢 5]

2. 對最有趣的結果使用 web_fetch 閱讀全文

3. 寫入：~/.openclaw/workspace/intel/$(date +%Y-%m-%d)-{你的領域}.md

## 輸出格式
# {你的領域}研究員 - [日期]

## 主要發現
- **[標題]** — [1-2 句話，附來源網址]
...

## 邊緣信號
[1 句話：目前這個領域大多數人完全忽略的事情]

## 連接到
[1 句話：如何與其他領域連結]

不要加狀態標籤如 CONFIRMED、UNCONFIRMED 或表情指示符。直接撰寫發現。
```

### 第五步 — 加入流水線腳本

在 `web/translate-all.sh` 中加入你的領域：
```bash
"$BASE/researchers/你的領域/findings/$DATE.md"
```

在 `web/scrape-all-images.sh` 中加入：
```python
RESEARCHERS = [
    ...
    "你的領域",
    ...
]
```

在 `intel-autopush` 排程的複製步驟中加入：
```bash
for domain in ... 你的領域; do
```

### 第六步 — 立即執行（可選）

```bash
# 立即觸發今日發現
openclaw cron run <cron-id>

# 複製到研究員資料夾
cp ~/.openclaw/workspace/intel/$(date +%Y-%m-%d)-你的領域.md \
   researchers/你的領域/findings/$(date +%Y-%m-%d).md

# 翻譯
python3 web/translate.py researchers/你的領域/findings/$(date +%Y-%m-%d).md

# 抓取圖片
python3 web/scrape-images.py researchers/你的領域/findings/$(date +%Y-%m-%d).md

# 部署
git add -A && git commit -m "feat: add 你的領域" && git push origin main
vercel deploy --prod
```

---

## ✏️ 精煉研究員提示詞

每個研究員的行為完全由其排程訊息控制。改進研究員的方式：

```bash
openclaw cron edit <cron-id> --message "$(cat researchers/{領域}/INSTRUCTIONS.md)"
```

**更好提示詞的技巧：**
- **查詢要具體** — 模糊的查詢只會得到主流新聞。精確的查詢才能獲得信號。
- **指定來源** — 告訴研究員哪些網站具有權威性（例如「優先使用 Bellingcat、ISW、CoinDesk 而非一般新聞」）
- **定義邊緣信號** — 明確說明「大多數人忽略的事」對你的領域意味著什麼
- **加入負面指令** — 「跳過財報」、「忽略新聞稿」、「不要引用維基百科」

---

## 🧠 精煉綜合代理人

綜合代理人讀取所有每日發現並連結跨領域線索。編輯 `synthesis/INSTRUCTIONS.md` 來改變：

- 優先考慮哪些領域
- 簡報格式與長度
- 「邊緣」框架（例如 加密貨幣 × AI × 地緣政治）
- 傳送到 Telegram 的輸出結構

更新即時排程：
```bash
openclaw cron edit <synthesis-cron-id> --message "$(cat synthesis/INSTRUCTIONS.md)"
```

---

## 👁️ 精煉首席分析師

首席分析師接收綜合輸出並產生最終可執行的簡報。編輯 `chief/INSTRUCTIONS.md` 來改變：

- 語調（更緊迫 vs. 更分析性）
- 「可執行」對你的使用案例意味著什麼
- 如何框架投資/策略意涵
- 輸出格式

```bash
openclaw cron edit <chief-cron-id> --message "$(cat chief/INSTRUCTIONS.md)"
```

---

## 🌏 新增子領域分頁（例如共產國家）

對於需要在一個領域內有多個國家/主題分頁的情況：

在 `web/server.py` 中，為你的研究員項目加入 `subs`：

```python
{"id": "你的群組", "emoji": "🌐", "name": "Your Group", "zh": "你的群組", "colors": "#111,#333",
 "subs": [
     {"id": "子主題1", "emoji": "🔵", "name": "Subtopic 1", "zh": "子主題一"},
     {"id": "子主題2", "emoji": "🔴", "name": "Subtopic 2", "zh": "子主題二"},
 ]},
```

每個子主題需要自己的研究員資料夾、排程任務和發現檔案。父領域頁面將自動渲染分頁導航。

---

## 🗑️ 移除領域

1. 從 `web/server.py` 的 `RESEARCHERS` 列表中移除
2. 刪除排程：`openclaw cron delete <cron-id>`
3. 從 `web/translate-all.sh` 和 `web/scrape-all-images.sh` 中移除
4. 可選擇性地封存發現資料夾

---

## 翻譯說明

翻譯通過 `web/translate.py` 使用 Claude Haiku 自動執行。如果某個領域的中文翻譯看起來有問題：

```bash
# 強制重新翻譯
touch researchers/{領域}/findings/{日期}.md
python3 web/translate.py researchers/{領域}/findings/{日期}.md
```

---

## 部署

每次對 repo 的更改都通過 `intel-autopush` 排程在 08:00 HKT 觸發，或手動執行：

```bash
git add -A && git commit -m "你的訊息" && git push origin main
vercel deploy --prod
```
