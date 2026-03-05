# 世界監控 API 情報報告
> [`koala73/worldmonitor`](https://github.com/koala73/worldmonitor) 的完整掃描——提取每個 API、資料來源和抓取方法，按 Intel Swarm 域分類，並評估集成價值。

---

## 摘要

World Monitor 在 22 個伺服器模組中使用**31 個不同的外部 API/資料來源**。幾乎所有都是免費或免費增值版本，需要 API 金鑰註冊。它們共同涵蓋衝突事件、軍事行動、海事運輸、網路威脅、經濟數據、預測市場、自然災害和即時新聞——直接對應 Intel Swarm 的 19 個研究域。

---

## 環境變數 → API

| 環境變數 | API / 服務 | 免費層級 | 需要金鑰 |
|---|---|---|---|
| `ACLED_ACCESS_TOKEN` | Armed Conflict Location & Event Data (ACLED) | ✅ 免費 (研究人員) | ✅ 是 |
| `FRED_API_KEY` | Federal Reserve Economic Data (FRED) | ✅ 免費 | ✅ 是 |
| `NASA_FIRMS_API_KEY` | NASA FIRMS (野火/火災偵測) | ✅ 免費 | ✅ 是 |
| `EIA_API_KEY` | US Energy Information Administration | ✅ 免費 | ✅ 是 |
| `FINNHUB_API_KEY` | Finnhub (股票市場資料) | ✅ 免費層級 | ✅ 是 |
| `CLOUDFLARE_API_TOKEN` | Cloudflare Radar (網際網路中斷) | ✅ 免費 | ✅ 是 |
| `GROQ_API_KEY` | Groq LLM 推論 (llama-3.1-8b-instant) | ✅ 免費層級 | ✅ 是 |
| `OPENROUTER_API_KEY` | OpenRouter (多模型 LLM 後備) | 💰 按使用量付費 | ✅ 是 |
| `OTX_API_KEY` | AlienVault OTX (網路威脅情報) | ✅ 免費 | ✅ 是 |
| `ABUSEIPDB_API_KEY` | AbuseIPDB (惡意 IP 報告) | ✅ 免費層級 | ✅ 是 |
| `URLHAUS_AUTH_KEY` | URLhaus (惡意軟體 URL 源) | ✅ 免費 | ✅ 是 |
| `WTO_API_KEY` | WTO (關稅、貿易流量) | ✅ 免費 | ✅ 是 |
| `AVIATIONSTACK_API` | Aviationstack (航班追蹤) | ✅ 免費層級 | ✅ 是 |
| `ICAO_API_KEY` | ICAO (導航警告/NOTAM) | ✅ 免費 | ✅ 是 |
| `TRAVELPAYOUTS_API_TOKEN` | Travelpayouts (航班價格) | ✅ 免費 | ✅ 是 |
| `WINGBITS_API_KEY` | Wingbits (眾包 ADS-B) | ✅ 免費 | ✅ 是 |
| `OLLAMA_*` | Ollama (本地 LLM) | ✅ 自託管 | ❌ 否 |
| `FIRMS_API_KEY` | NASA FIRMS (別名) | ✅ 免費 | ✅ 是 |

**無需金鑰的 API (完全公開):**
- OpenSky Network (透過 ADS-B 的軍事航班追蹤)
- USGS Earthquake Feed
- NASA EONET (自然事件)
- GDACS (全球災難警報)
- CoinGecko (加密貨幣報價)
- Yahoo Finance (商品、ETF、宏觀信號、Fear & Greed Index)
- Alternative.me (Fear & Greed Index)
- arXiv (研究論文)
- Hacker News (RSS)
- GDELT DOC API (新聞文檔)
- GDELT GEO API (地理定位事件)
- UCDP (烏普薩拉武裝衝突資料)
- Gamma API / Polymarket (預測市場)
- RSS 源 (100+ 精選新聞來源)

## 完整 API 目錄（按 Intel Swarm 領域分類）

### ⚔️ 戰爭

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **ACLED** | 戰役、爆炸、針對平民的暴力——精確的經緯度、傷亡人數、參與者、日期 | `https://acleddata.com/api/acled/read` | ✅ 免費 | 15 分鐘快取 |
| **UCDP** | 烏普薩拉武裝衝突資料庫——國家間暴力、片面暴力 | 從烏普薩拉 API 定期獲取 | ❌ 否 | 每日 |
| **GDELT GEO** | 地理定位新聞事件——帶有座標的衝突文章、語氣評分 | `https://api.gdeltproject.org/api/v2/geo/geo` | ❌ 否 | 15 分鐘 |
| **GDELT DOC** | 新聞文章搜尋——衝突、軍事、戰爭關鍵字篩選 | `https://api.gdeltproject.org/api/v2/doc/doc` | ❌ 否 | 15 分鐘 |
| **OpenSky** | 軍用飛機追蹤——呼號/十六進位篩選、劇院邊界框（波羅的海→葉門、太平洋） | `https://opensky-network.org/api/states/all` | ❌ 否 | 10 分鐘 |
| **Wingbits** | 眾包 ADS-B（OpenSky 備用）——覆蓋高衝突地區的盲點 | 透過中繼 | ✅ 免費 | 10 分鐘 |
| **NASA EONET** | 與衝突相關的活躍自然事件（戰爭區附近的火災） | `https://eonet.gsfc.nasa.gov/api/v3/events` | ❌ 否 | 1 小時 |
| **OREF Israel** | 以色列即時火箭/飛彈警報——特定位置警報 | `https://www.oref.org.il/` | ❌ 否 | 即時 |
| **RSS: BBC/Al Jazeera/Reuters/Guardian ME** | 戰爭新聞源、中東報導 | 多個 RSS | ❌ 否 | 15 分鐘 |

**🎯 這對 Intel Swarm 戰爭領域的補充：**
- 具有精確座標的即時戰場事件 → 為衝突地圖提供支持
- 跨 9 個軍事劇院（波羅的海、波斯灣、南中國海等）的劇院態勢追蹤
- 以色列飛彈警報整合
- 軍用飛機類型分類（AWACS、油機、ISR、打擊）

---

### 📦  大宗商品

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **Yahoo Finance** | 油（CL=F）、黃金（GC=F）、天然氣（NG=F）、小麥（ZW=F）、銅（HG=F）、白銀（SI=F）期貨價格 + 迷你圖 | `https://query1.finance.yahoo.com/v8/finance/chart` | ❌ 否 | 10 分鐘 |
| **FRED** | 運費率（FRED 序列：WTISPLC）、波羅的海乾散貨運價指數代理、大宗商品通膨 | `https://api.stlouisfed.org/fred/series/observations` | ✅ 免費 | 1 小時 |
| **EIA** | 美國能源：原油產量、天然氣儲存、煉油能力、管道流量 | `https://api.eia.gov/` | ✅ 免費 | 每日 |
| **BIS** | 大宗商品貨幣匯率（AUD、CAD、NOK——大宗商品掛鉤） | `https://stats.bis.org/api/v2/` | ❌ 否 | 每月 |
| **Supply Chain: Chokepoint Status** | 霍爾木茲、曼德海峽、蘇伊士、馬六甲、博斯普魯斯海峽、巴拿馬狀態——根據 AIS + NOTAM 資料評分 | 內部計算 | — | 5 分鐘 |
| **ICAO/NOTAM** | 油輪運輸航道附近的導航警告 | ICAO 代理 | ✅ 免費 | 30 分鐘 |
| **Maritime AIS** | 卡脖子位置的船隻密度——中斷偵測（間隔尖峰、擁塞） | 透過中繼（MarineTraffic 風格） | 中繼 | 5 分鐘 |
| **Critical Minerals** | 稀土、鋰、鈷供應中斷追蹤 | USGS/內部 | — | 每週 |
| **Shipping Rates** | FRED WCSR（世界集裝箱運價）、Drewry 指數透過 FRED | FRED | ✅ 免費 | 每週 |

**🎯 這對以下的補充：**
- 即時卡脖子威脅評分（霍爾木茲 = 目前危急）
- 海峽的船隻密度異常偵測
- 終端機頁面的真實大宗商品期貨與迷你圖

---

### 🇷🇺 俄羅斯 / 🇨🇳 中國 / 🇰🇵 北韓（共產主義國家）

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **ACLED** | 俄烏戰場事件、中國抗議事件、朝鮮半島邊境事件 | ACLED API | ✅ 免費 | 15 分鐘 |
| **UCDP** | 按國家篩選的歷史武裝衝突資料 | 烏普薩拉 | ❌ 否 | 每日 |
| **GDELT DOC** | 俄羅斯/中國/朝鮮半島官方媒體監控、關鍵字篩選 | GDELT | ❌ 否 | 15 分鐘 |
| **WTO** | 俄羅斯、中國應用的關稅率（後制裁追蹤） | `https://stats.wto.org/SDMX/` | ✅ 免費 | 每年 |
| **Trade Flows (WTO)** | 出口/進口雙邊流量中國↔美國、俄羅斯↔歐盟 | WTO API | ✅ 免費 | 每年 |
| **FRED** | 俄羅斯盧布（DEXRUUS）、中國人民幣（DEXCHUS）匯率 | FRED | ✅ 免費 | 每日 |
| **BIS** | 央行政策利率：俄羅斯（CBR）、中國（PBoC） | BIS SDMX | ❌ 否 | 每月 |
| **OpenSky** | 俄羅斯/中國軍用飛機近劇院邊界 | OpenSky | ❌ 否 | 10 分鐘 |
| **RSS: BBC/Reuters/Guardian/Al Jazeera** | 篩選的俄羅斯/中國/朝鮮半島報導 | RSS | ❌ 否 | 15 分鐘 |

**🎯 這對以下的補充：**
- 顯示制裁影響的實際雙邊貿易流量資料
- 央行利率追蹤（CBR 緊急升息 = 危機信號）
- 軍用飛機在爭議領土附近的位置確定

---

### 📈  宏觀經濟

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **FRED** | 200+ 序列：GDP、CPI、失業率、M2、10 年期收益率、收益率曲線、PCE、住房 | FRED API | ✅ 免費 | 1 小時 |
| **BIS** | 央行政策利率（聯準會、歐洲央行、日本央行、英國央行、PBoC、RBA、瑞銀、加拿大央行） | BIS SDMX WS_CBPOL | ❌ 否 | 每月 |
| **BIS Credit** | 民間部門信貸/GDP 比率（金融穩定性指標） | BIS SDMX | ❌ 否 | 季度 |
| **BIS FX** | 主要貨幣匯率 | BIS SDMX | ❌ 否 | 每月 |
| **Yahoo Finance Macro Signals** | 日圓/美元、BTC、QQQ、XLP（主食 ETF）、VIX 代理——跨資產風險信號 | Yahoo Finance | ❌ 否 | 每日 |
| **Alternative.me** | 加密貨幣恐懼與貪婪指數（0–100）——風險開/關信號 | `https://api.alternative.me/fng/` | ❌ 否 | 每日 |
| **Finnhub** | 股票市場資料、收益、公司信號 | `https://finnhub.io/api/v1` | ✅ 免費 | 即時 |
| **WTO** | 貿易限制指數、按國家的關稅趨勢 | WTO API | ✅ 免費 | 每年 |
| **FRED: WCSR** | 世界集裝箱運價（供應鏈壓力） | FRED | ✅ 免費 | 每週 |
| **RSS: FT/CNBC/WSJ/MarketWatch/Bloomberg** | 宏觀經濟新聞源 | RSS | ❌ 否 | 15 分鐘 |

**🎯 這對以下的補充：**
- 來自 FRED 的完整收益率曲線（2 年/5 年/10 年/30 年價差）
- 央行政策發散追蹤（聯準會 vs 日本央行 = 日圓套利風險）
- 恐懼與貪婪指數作為交易者的宏觀情緒信號

---

### ₿ 加密貨幣

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **CoinGecko** | BTC、ETH、SOL、XRP、DOGE、PEPE 價格、24 小時漲幅、市值、成交量 | `https://api.coingecko.com/api/v3/coins/markets` | ❌ 否 | 10 分鐘 |
| **Yahoo Finance** | BTC-USD 歷史圖表、ETF（IBIT、FBTC）流量 | Yahoo Finance | ❌ 否 | 每日 |
| **Gamma/Polymarket** | 加密貨幣相關事件的預測市場（BTC ATH、ETF 批准等） | Gamma API | ❌ 否 | 10 分鐘 |
| **Alternative.me** | 恐懼與貪婪指數——加密貨幣情緒 | API | ❌ 否 | 每日 |
| **Stablecoin Markets** | USDT、USDC 脫鉤監控、穩定幣流動性 | Yahoo Finance 行情 | ❌ 否 | 10 分鐘 |
| **ETF Flows** | IBIT、FBTC、ARKB、BTCO、HODL——現貨 BTC ETF 流量追蹤 | Yahoo Finance | ❌ 否 | 每日 |
| **RSS: CoinDesk/CoinTelegraph/The Block** | 加密貨幣新聞 | RSS | ❌ 否 | 15 分鐘 |

**🎯 這對以下的補充：**
- 終端機頁面上的即時加密貨幣價格與迷你圖
- 穩定幣脫鉤監控（USDT 脫鉤 = 系統性風險）
- ETF 流量追蹤（機構情緒）
- 加密貨幣事件的預測市場

---

### 🤖 AI 代理 / 🌀  奇異點

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **arXiv** | AI/機器學習研究論文——`cs.AI`、`cs.LG`、`cs.CL`、`stat.ML` 類別 | `https://export.arxiv.org/api/query` | ❌ 否 | 1 小時 |
| **GitHub Trending** | 熱門 AI 倉庫（星星/分叉信號） | GitHub RSS/抓取 | ❌ 否 | 每日 |
| **Hacker News** | AI/科技討論、Show HN、Ask HN | `https://hnrss.org/frontpage` | ❌ 否 | 15 分鐘 |
| **RSS: VentureBeat AI/MIT Tech Review/The Verge AI/Ars Technica** | AI 新聞源 | RSS | ❌ 否 | 15 分鐘 |
| **arXiv RSS** | `cs.AI` RSS 源——直接來自 arXiv | `https://export.arxiv.org/rss/cs.AI` | ❌ 否 | 每日 |
| **Groq** | 用於 AI 事件分類、摘要的 LLM 推論 | Groq API | ✅ 免費 | 隨需 |
| **Ollama** | 本機 LLM 備用（llama3、mistral、qwen） | 本機 | ❌ 否 | 隨需 |
| **OpenRouter** | 多模型 LLM 備用鏈 | OpenRouter API | 💰 付費 | 隨需 |
| **Tech Events** (Eventbrite/Meetup proxy) | AI/科技會議日曆 | 抓取 | ❌ 否 | 每日 |

**🎯 這對以下的補充：**
- arXiv 論文監控——新模型版本（DeepSeek、Llama 等）在新聞前發佈在 arXiv
- HackerNews 信號——社群對 AI 發展的反應
- 熱門 GitHub 倉庫——新 AI 工具/框架的早期信號

---

### 🏥 健康

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **NASA EONET** | 疾病爆發相關事件（洪水 → 霍亂等） | EONET API | ❌ 否 | 1 小時 |
| **GDACS** | 具有人道主義影響的災難警報（與疾病風險相關聯） | `https://www.gdacs.org/gdacsapi/` | ❌ 否 | 1 小時 |
| **ACLED** | 針對衛生保健設施附近平民的暴力 | ACLED | ✅ 免費 | 15 分鐘 |
| **FRED** | 健康支出指標、製藥價格指數 | FRED | ✅ 免費 | 每年 |
| **RSS: WHO/Reuters Health/STAT News** | 健康新聞、爆發警報 | RSS | ❌ 否 | 15 分鐘 |
| **Displacement Summary** | UNHCR 流離失所資料（難民 → 公共衛生危機） | UNHCR 相關 | ❌ 否 | 每週 |

**🎯 這對以下的補充：**
- 自然災害 → 疾病爆發早期預警（洪水 + 流離失所 = 霍亂風險）
- WHO 警報監控通過 RSS

---

### 🔍 陰謀論 / 📁 愛潑斯坦 / 🕵️ 黑預算

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **GDELT DOC** | 關鍵字搜尋：「深層政府」、「舉報人」、「機密」、「FOIA」、「解密」 | GDELT API | ❌ 否 | 15 分鐘 |
| **FRED: USA Spending** | 美國聯邦可斌配支出、黑預算代理 | USA Spending API（透過 FRED） | ❌ 否 | 每年 |
| **RSS: The Intercept/ProPublica/Substack** | 調查新聞源 | RSS | ❌ 否 | 15 分鐘 |
| **arXiv** | 監控技術論文（`cs.CR` 安全、密碼學） | arXiv | ❌ 否 | 1 小時 |
| **Cyber Threats (OTX/URLhaus)** | 國家級網路攻擊操作（五眼聯盟、GRU、APT 組織） | OTX/URLhaus | ✅ 免費 | 2 小時 |

**🎯 這對以下的補充：**
- 透過 USA Spending API 的政府支出異常偵測
- 國家級網路攻擊操作追蹤（歸因於民族國家參與者）

---

### 💼 量化 / 📊 西方東方 / 🌐 新興市場

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **Yahoo Finance** | 國家股票指數：日經、上證、恆生、富時、DAX、聖保羅 | Yahoo Finance | ❌ 否 | 每日 |
| **BIS** | 按國家的信貸/GDP 比率、匯率、政策利率 | BIS SDMX | ❌ 否 | 每月 |
| **FRED** | 新興市場主權收益率、貨幣對（巴西雷亞爾、印度盧比、土耳其里拉、南非蘭特） | FRED | ✅ 免費 | 每日 |
| **WTO Trade Flows** | 雙邊貿易流量——中國↔東盟、美國↔歐盟等 | WTO API | ✅ 免費 | 每年 |
| **WTO Tariff Trends** | 按報告者/夥伴國家應用的 MFN 關稅率 | WTO API | ✅ 免費 | 每年 |
| **WTO Trade Restrictions** | 與制裁相關的貿易壁壘 | WTO API | ✅ 免費 | 每月 |
| **World Bank** | GDP、通膨、貧困、FDI、人口指標 | WB API | ❌ 否 | 每年 |
| **Gulf FDI** (config) | 阿聯酋、沙烏地、卡達 FDI 流入追蹤 | 內部組態資料 | — | — |
| **Gulf Market Quotes** | TADAWUL（沙烏地）、ADX（阿聯酋）、DSM（卡達）指數 | Yahoo Finance 行情 | ❌ 否 | 每日 |
| **Finnhub** | 部門級股票表現、收益日曆 | Finnhub | ✅ 免費 | 即時 |
| **ETF Flows** | EEM、VWO（新興市場 ETF）流量 | Yahoo Finance | ❌ 否 | 每日 |

**🎯 這對以下的補充：**
- 實際雙邊貿易流量數據（例如美中貿易量同比下降）
- 新興市場主權收益率追蹤（土耳其、巴西壓力信號）
- 宏觀領域的灣灣股票市場整合

---

### ✊ 文化 / 🏆 體育

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **ACLED** | 抗議事件（文化/政治）及其位置 | ACLED | ✅ 免費 | 15 分鐘 |
| **GDELT DOC** | 文化事件關鍵字搜尋 | GDELT | ❌ 否 | 15 分鐘 |
| **RSS: Entertainment/Sports feeds** | 奧斯卡、葛萊美、NFL、NBA、英超 | RSS | ❌ 否 | 15 分鐘 |
| **Positive Events** | 保護成果、科學突破、外交進展 | EONET + GDELT | ❌ 否 | 1 小時 |

---

### ✝️ 宗教

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **ACLED** | 宗教暴力事件——按 `sub_event_type` 篩選 | ACLED | ✅ 免費 | 15 分鐘 |
| **GDELT DOC** | 宗教衝突關鍵字搜尋（聖戰、十字軍、迫害、褻瀆） | GDELT | ❌ 否 | 15 分鐘 |
| **OREF Sirens** | 以色列飛彈警報——與宗教民族主義衝突相關聯 | OREF | ❌ 否 | 即時 |
| **RSS: Al Jazeera/Vatican News/Times of Israel** | 宗教相關新聞報導 | RSS | ❌ 否 | 15 分鐘 |

## 獨家高價值 API（目前未在 Intel Swarm 中）

以下是最有影響力的新集成需要考慮：

### 🔴 優先級 1 — 現在構建

| API | 它解鎖了什麼 | 免費？ |
|---|---|---|
| **ACLED** | 具有精確坐標的真實戰場事件 → 真實衝突地圖數據 | ✅ 免費（註冊） |
| **FRED** | 收益率曲線、美聯儲政策、通貨膨脹 — 為宏觀 + 量化領域提供動力 | ✅ 免費 |
| **CoinGecko** | 帶有火花線的實時加密價格 → 終端頁面 | ✅ 免費 |
| **Yahoo Finance** | 商品期貨、國家指數、ETF 流動 | ✅ 免費（無需密鑰） |
| **arXiv** | AI 論文監控 — DeepSeek/Llama 論文在此出現早於新聞 | ✅ 免費 |
| **Alternative.me** | Fear & Greed Index — 單個 API 調用，巨大信號價值 | ✅ 免費 |
| **OREF** | 以色列導彈警報器 → 實時戰爭警報 | ✅ 免費 |

### 🟡 優先級 2 — 註冊和集成

| API | 它解鎖了什麼 | 註冊 |
|---|---|---|
| **GDELT GEO (fix)** | 具有正確事件坐標的熱力圖（不是 CSV 參與者代碼） | ❌ 無密鑰 |
| **NASA FIRMS** | 活躍火災檢測 → 戰爭相關縱火、基礎設施火災 | ✅ 免費在 earthdata.nasa.gov |
| **USGS Earthquakes** | 地震事件 → 採礦/基礎設施中斷信號 | ❌ 無密鑰 |
| **NASA EONET** | 開放的自然事件：風暴、洪水、火山噴發 | ❌ 無密鑰 |
| **Cloudflare Radar** | 按國家/地區的互聯網中斷 → 數字戰爭、審查信號 | ✅ 免費在 dash.cloudflare.com |
| **OTX AlienVault** | 網絡威脅指標 — 國家級 APT 組織 | ✅ 免費在 otx.alienvault.com |
| **WTO API** | 關稅率、貿易壁壘 — 宏觀/西東 | ✅ 免費在 api.wto.org |
| **BIS SDMX** | 央行政策率 — 宏觀/量化 | ❌ 無密鑰 |
| **World Bank** | 新興市場經濟指標 | ❌ 無密鑰 |
| **Finnhub** | 股票數據、收益 — 量化/宏觀 | ✅ 免費在 finnhub.io |

### 🟢 優先級 3 — 準備就緒時付費

| API | 它解鎖了什麼 | 成本 |
|---|---|---|
| **ACLED full access** | 10 年衝突歷史、所有事件類型 | 免費進行研究註冊 |
| **OpenSky** | 全球軍事飛行追蹤 | 免費（帳戶用於更高的速率限制） |
| **EIA** | 美國能源數據（石油、天然氣、電網） | ✅ 免費在 eia.gov |
| **Finnhub** | 實時股票報價 | 免費層 + 實時付費 |
| **Groq** | 用於分類的超快速 LLM 推理 | 免費層 |

---

## LLM 架構（World Monitor 模式）

World Monitor 使用值得採納的 3 層 LLM 後備鏈：

```
1. Groq (llama-3.1-8b-instant) — 最快、最便宜、足以用於分類
2. Ollama（本地模型） — 當 Groq 失敗或用於敏感數據時
3. OpenRouter → Claude/GPT-4 — 僅用於複雜推理任務
```

**World Monitor 中的用例：**
- `classify-event.ts` — 將新聞事件分類為 CONFLICT/PROTEST/POLITICAL/NATURAL
- `deduct-situation.ts` — 多源"真正發生了什麼"的綜合
- `get-country-intel-brief.ts` — 按國家 LLM 生成的情報簡報
- `summarize-article.ts` — 文章摘要管道
- `search-gdelt-documents.ts` — 對 GDELT 結果的語義搜索

**→ 對於 Intel Swarm：** 此模式直接映射到我們的研究人員管道。可以用 Groq 替換或增強當前基於 Sonnet 的研究人員以提高速度 + 降低成本，為首席綜合保留 Opus。

---

## 使用的抓取方法

| 方法 | 用於 | 注釋 |
|---|---|---|
| **RSS 解析** | 100+ 跨所有域的新聞源 | 在 `_feeds.ts` 中策展、8 個類別 |
| **Yahoo Finance 抓取** | 商品、ETF 流動、宏觀信號、國家指數 | 使用 `yahooGate()` 順序速率限制器避免 429 |
| **OpenSky ADS-B** | 軍事飛行檢測 | 按呼號模式 + 十六進制代碼數據庫過濾 |
| **OREF 抓取** | 以色列導彈警報器 | 直接 HTML 抓取 oref.org.il |
| **GDELT CSV 下載** | 帶有 lat/lng 的衝突事件 | `lastupdate.txt` → ZIP → CSV 管道 |
| **GPS Jam 抓取** | GPS 干擾區（欺騙/干擾） | `gpsjam.org` 數據 |
| **USNI 抓取** | 美國海軍艦隊報告 | 海軍學會新聞抓取 |
| **Wingbits 中繼** | OpenSky 宕機時的 ADS-B 備份 | WebSocket 中繼 |

---

## RSS 源目錄（World Monitor `_feeds.ts`）

100+ 源跨 8 個類別 — 在 Intel Swarm 中立即可用：

**政治/世界：** BBC World, Guardian, AP, Reuters, CNN, France24, EuroNews, Le Monde, DW, Al Jazeera, BBC Middle East, Oman Observer

**美國：** NPR, PBS NewsHour, ABC, CBS, NBC, WSJ, Politico, The Hill, Axios

**技術：** Hacker News, Ars Technica, The Verge, MIT Tech Review

**AI：** VentureBeat AI, The Verge AI, MIT Tech Review AI, ArXiv cs.AI

**金融：** CNBC, MarketWatch, Yahoo Finance, FT, Bloomberg RSS 代理

**科學：** Nature, Science AAAS, New Scientist, Scientific American

**加密貨幣：** CoinDesk, CoinTelegraph, The Block, Decrypt

**軍事/防禦：** War on the Rocks, Defense One, USNI News, Bellingcat

---

## 推薦集成路線圖

### 第 1 階段（本週）— 零成本、無新密鑰
1. **CoinGecko** → 終端 + 加密領域上的實時加密價格
2. **Yahoo Finance** → 商品期貨 + 國家股票指數 + ETF 流動
3. **arXiv cs.AI** → AI Agents 領域的實時 AI 論文監控
4. **Alternative.me Fear & Greed** → 單個指標、巨大宏觀信號
5. **BIS SDMX** → 宏觀領域的央行政策率
6. **USGS** → 衝突地圖 + 黑預算領域的地震源
7. **NASA EONET** → 自然事件源

### 第 2 階段（免費密鑰註冊）
1. **ACLED** → 在衝突地圖上用真實衝突事件替換虛假 GDELT 參與者代碼
2. **FRED** → 完整的宏觀數據層（收益率曲線、CPI、M2 貨幣供應）
3. **NASA FIRMS** → 野火/活躍火災檢測
4. **Cloudflare Radar** → 互聯網中斷監控（BlackBudget/War 領域）
5. **OTX AlienVault** → BlackBudget 域的網絡威脅情報
6. **Finnhub** → Quant 域的股票報價
7. **EIA** → 商品領域的能源數據
8. **WTO** → WestEast + Macro 的關稅/貿易數據

### 第 3 階段（基礎設施）
1. **Groq LLM** → 快速分類器用於突發新聞事件分類
2. **OpenSky** → 衝突地圖上的軍事飛行追蹤
3. **OREF** → 以色列導彈警報器實時警報
4. **GPS Jam** → GPS 欺騙區（軍事活動信號）
5. **USNI** → 美國艦隊態勢報告

---

*由 CD（Intel Swarm）生成 — 完整掃描 `koala73/worldmonitor` 提交歷史和服務器模塊目錄。最後更新：2026-03-05。*

