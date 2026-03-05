# World Monitor API Intelligence Report
> Full scan of [`koala73/worldmonitor`](https://github.com/koala73/worldmonitor) — every API, data source, and scraping method extracted, classified by Intel Swarm domain, and rated for integration value.

---

## Summary

World Monitor uses **31 distinct external APIs/data sources** across 22 server modules. Almost all are free or freemium with API key registration. Together they cover conflict events, military movements, maritime shipping, cyber threats, economic data, prediction markets, natural disasters, and live news — directly mapping to Intel Swarm's 19 research domains.

---

## Environment Variables → APIs

| Env Var | API / Service | Free Tier | Key Required |
|---|---|---|---|
| `ACLED_ACCESS_TOKEN` | Armed Conflict Location & Event Data (ACLED) | ✅ Free (researcher) | ✅ Yes |
| `FRED_API_KEY` | Federal Reserve Economic Data (FRED) | ✅ Free | ✅ Yes |
| `NASA_FIRMS_API_KEY` | NASA FIRMS (wildfire/fire detections) | ✅ Free | ✅ Yes |
| `EIA_API_KEY` | US Energy Information Administration | ✅ Free | ✅ Yes |
| `FINNHUB_API_KEY` | Finnhub (stock market data) | ✅ Free tier | ✅ Yes |
| `CLOUDFLARE_API_TOKEN` | Cloudflare Radar (internet outages) | ✅ Free | ✅ Yes |
| `GROQ_API_KEY` | Groq LLM inference (llama-3.1-8b-instant) | ✅ Free tier | ✅ Yes |
| `OPENROUTER_API_KEY` | OpenRouter (multi-model LLM fallback) | 💰 Pay-per-use | ✅ Yes |
| `OTX_API_KEY` | AlienVault OTX (cyber threat intel) | ✅ Free | ✅ Yes |
| `ABUSEIPDB_API_KEY` | AbuseIPDB (malicious IP reports) | ✅ Free tier | ✅ Yes |
| `URLHAUS_AUTH_KEY` | URLhaus (malware URL feed) | ✅ Free | ✅ Yes |
| `WTO_API_KEY` | WTO (tariffs, trade flows) | ✅ Free | ✅ Yes |
| `AVIATIONSTACK_API` | Aviationstack (flight tracking) | ✅ Free tier | ✅ Yes |
| `ICAO_API_KEY` | ICAO (navigational warnings/NOTAMs) | ✅ Free | ✅ Yes |
| `TRAVELPAYOUTS_API_TOKEN` | Travelpayouts (flight prices) | ✅ Free | ✅ Yes |
| `WINGBITS_API_KEY` | Wingbits (crowdsourced ADS-B) | ✅ Free | ✅ Yes |
| `OLLAMA_*` | Ollama (local LLM) | ✅ Self-hosted | ❌ No |
| `FIRMS_API_KEY` | NASA FIRMS (alias) | ✅ Free | ✅ Yes |

**No-key APIs (fully public):**
- OpenSky Network (military flight tracking via ADS-B)
- USGS Earthquake Feed
- NASA EONET (natural events)
- GDACS (global disaster alerts)
- CoinGecko (crypto quotes)
- Yahoo Finance (commodities, ETF, macro signals, Fear & Greed Index)
- Alternative.me (Fear & Greed Index)
- arXiv (research papers)
- Hacker News (RSS)
- GDELT DOC API (news documents)
- GDELT GEO API (geolocated events)
- UCDP (Uppsala armed conflict data)
- Gamma API / Polymarket (prediction markets)
- RSS feeds (100+ curated news sources)

---

## Full API Catalogue by Intel Swarm Domain

---

### ⚔️ WAR

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **ACLED** | Battles, explosions, violence against civilians — exact lat/lng, fatalities, actors, date | `https://acleddata.com/api/acled/read` | ✅ Free | 15 min cache |
| **UCDP** | Uppsala armed conflict database — state-based violence, one-sided violence | Cron-seeded from Uppsala API | ❌ No | Daily |
| **GDELT GEO** | Geolocated news events — conflict articles with coordinates, tone score | `https://api.gdeltproject.org/api/v2/geo/geo` | ❌ No | 15 min |
| **GDELT DOC** | News article search — conflict, military, war keyword filtering | `https://api.gdeltproject.org/api/v2/doc/doc` | ❌ No | 15 min |
| **OpenSky** | Military aircraft tracking — callsign/hex filtering, theater bounding boxes (Baltic→Yemen, Pacific) | `https://opensky-network.org/api/states/all` | ❌ No | 10 min |
| **Wingbits** | Crowdsourced ADS-B (OpenSky fallback) — covers blind spots in high-conflict zones | Via relay | ✅ Free | 10 min |
| **NASA EONET** | Active conflict-linked natural events (fires near war zones) | `https://eonet.gsfc.nasa.gov/api/v3/events` | ❌ No | 1h |
| **OREF Israel** | Israeli real-time rocket/missile sirens — location-specific alerts | `https://www.oref.org.il/` | ❌ No | Real-time |
| **RSS: BBC/Al Jazeera/Reuters/Guardian ME** | War news feeds, Middle East coverage | Multiple RSS | ❌ No | 15 min |

**🎯 What this adds to Intel Swarm WAR domain:**
- Real-time battlefield events with exact coordinates → power the Conflict Map
- Theater posture tracking across 9 military theaters (Baltic, Persian Gulf, SCS, etc.)
- Israeli missile alert integration
- Military aircraft type classification (AWACS, tanker, ISR, strike)

---

### 📦 COMMODITIES

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **Yahoo Finance** | Oil (CL=F), Gold (GC=F), Natural Gas (NG=F), Wheat (ZW=F), Copper (HG=F), Silver (SI=F) futures prices + sparklines | `https://query1.finance.yahoo.com/v8/finance/chart` | ❌ No | 10 min |
| **FRED** | Shipping rates (FRED series: WTISPLC), Baltic Dry Index proxy, commodity inflation | `https://api.stlouisfed.org/fred/series/observations` | ✅ Free | 1h |
| **EIA** | US energy: crude oil production, natural gas storage, refinery capacity, pipeline flows | `https://api.eia.gov/` | ✅ Free | Daily |
| **BIS** | Commodity currency exchange rates (AUD, CAD, NOK — commodity-linked) | `https://stats.bis.org/api/v2/` | ❌ No | Monthly |
| **Supply Chain: Chokepoint Status** | Hormuz, Bab-el-Mandeb, Suez, Malacca, Bosphorus, Panama status — scored from AIS + NOTAM data | Internal computation | — | 5 min |
| **ICAO/NOTAM** | Navigation warnings near oil shipping lanes | ICAO proxy | ✅ Free | 30 min |
| **Maritime AIS** | Vessel density at chokepoints — disruption detection (gap spikes, congestion) | Via relay (MarineTraffic-style) | Relay | 5 min |
| **Critical Minerals** | Rare earth, lithium, cobalt supply disruption tracking | USGS/internal | — | Weekly |
| **Shipping Rates** | FRED WCSR (World Container Shipping Rate), Drewry index via FRED | FRED | ✅ Free | Weekly |

**🎯 What this adds:**
- Live chokepoint threat scoring (Hormuz = CRITICAL right now)
- Vessel density anomaly detection at straits
- Real commodity futures with sparklines for the Terminal page

---

### 🇷🇺 RUSSIA / 🇨🇳 CHINA / 🇰🇵 NORTH KOREA (Communist States)

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **ACLED** | Russia/Ukraine battlefield events, China protest events, NK border incidents | ACLED API | ✅ Free | 15 min |
| **UCDP** | Historical armed conflict data filtered by country | Uppsala | ❌ No | Daily |
| **GDELT DOC** | Russian/Chinese/NK state media monitoring, keyword-filtered | GDELT | ❌ No | 15 min |
| **WTO** | Tariff rates applied by/against Russia, China (post-sanction tracking) | `https://stats.wto.org/SDMX/` | ✅ Free | Annual |
| **Trade Flows (WTO)** | Export/import bilateral flows China↔US, Russia↔EU | WTO API | ✅ Free | Annual |
| **FRED** | Russian ruble (DEXRUUS), Chinese yuan (DEXCHUS) exchange rates | FRED | ✅ Free | Daily |
| **BIS** | Central bank policy rates: Russia (CBR), China (PBoC) | BIS SDMX | ❌ No | Monthly |
| **OpenSky** | Russian/Chinese military aircraft near theater boundaries | OpenSky | ❌ No | 10 min |
| **RSS: BBC/Reuters/Guardian/Al Jazeera** | Filtered Russia/China/NK coverage | RSS | ❌ No | 15 min |

**🎯 What this adds:**
- Actual bilateral trade flow data showing sanction impact
- Central bank rate tracking (CBR emergency rate hikes = crisis signal)
- Military aircraft positioning near contested territories

---

### 📈 MACRO

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **FRED** | 200+ series: GDP, CPI, unemployment, M2, 10Y yield, yield curve, PCE, housing | FRED API | ✅ Free | 1h |
| **BIS** | Central bank policy rates (Fed, ECB, BoJ, BoE, PBoC, RBA, SNB, BoC) | BIS SDMX WS_CBPOL | ❌ No | Monthly |
| **BIS Credit** | Private sector credit/GDP ratios (financial stability indicator) | BIS SDMX | ❌ No | Quarterly |
| **BIS FX** | Major currency exchange rates | BIS SDMX | ❌ No | Monthly |
| **Yahoo Finance Macro Signals** | JPY/USD, BTC, QQQ, XLP (staples ETF), VIX proxy — cross-asset risk signal | Yahoo Finance | ❌ No | Daily |
| **Alternative.me** | Crypto Fear & Greed Index (0–100) — risk-on/off signal | `https://api.alternative.me/fng/` | ❌ No | Daily |
| **Finnhub** | Stock market data, earnings, company signals | `https://finnhub.io/api/v1` | ✅ Free | Real-time |
| **WTO** | Trade restriction index, tariff trends by country | WTO API | ✅ Free | Annual |
| **FRED: WCSR** | World container shipping rates (supply chain pressure) | FRED | ✅ Free | Weekly |
| **RSS: FT/CNBC/WSJ/MarketWatch/Bloomberg** | Macro news feeds | RSS | ❌ No | 15 min |

**🎯 What this adds:**
- Full yield curve (2Y/5Y/10Y/30Y spread) from FRED
- Central bank policy divergence tracking (Fed vs BoJ = JPY carry risk)
- Fear & Greed Index as a macro sentiment signal for traders

---

### ₿ CRYPTO

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **CoinGecko** | BTC, ETH, SOL, XRP, DOGE, PEPE prices, 24h change, market cap, volume | `https://api.coingecko.com/api/v3/coins/markets` | ❌ No | 10 min |
| **Yahoo Finance** | BTC-USD historical chart, ETF (IBIT, FBTC) flows | Yahoo Finance | ❌ No | Daily |
| **Gamma/Polymarket** | Prediction markets for crypto-related events (BTC ATH, ETF approval, etc.) | Gamma API | ❌ No | 10 min |
| **Alternative.me** | Fear & Greed Index — crypto sentiment | API | ❌ No | Daily |
| **Stablecoin Markets** | USDT, USDC depeg monitoring, stablecoin liquidity | Yahoo Finance tickers | ❌ No | 10 min |
| **ETF Flows** | IBIT, FBTC, ARKB, BTCO, HODL — spot BTC ETF flow tracking | Yahoo Finance | ❌ No | Daily |
| **RSS: CoinDesk/CoinTelegraph/The Block** | Crypto news | RSS | ❌ No | 15 min |

**🎯 What this adds:**
- Live crypto prices with sparklines directly on the Terminal page
- Stablecoin depeg monitoring (USDT depeg = systemic risk)
- ETF flow tracking (institutional sentiment)
- Prediction markets on crypto events

---

### 🤖 AI AGENTS / 🌀 SINGULARITY

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **arXiv** | AI/ML research papers — `cs.AI`, `cs.LG`, `cs.CL`, `stat.ML` categories | `https://export.arxiv.org/api/query` | ❌ No | 1h |
| **GitHub Trending** | Trending AI repos (stars/forks signal) | GitHub RSS/scrape | ❌ No | Daily |
| **Hacker News** | AI/tech discussions, Show HN, Ask HN | `https://hnrss.org/frontpage` | ❌ No | 15 min |
| **RSS: VentureBeat AI/MIT Tech Review/The Verge AI/Ars Technica** | AI news feeds | RSS | ❌ No | 15 min |
| **arXiv RSS** | `cs.AI` RSS feed — direct from arXiv | `https://export.arxiv.org/rss/cs.AI` | ❌ No | Daily |
| **Groq** | LLM inference for AI event classification, summarization | Groq API | ✅ Free | On-demand |
| **Ollama** | Local LLM fallback (llama3, mistral, qwen) | Local | ❌ No | On-demand |
| **OpenRouter** | Multi-model LLM fallback chain | OpenRouter API | 💰 Paid | On-demand |
| **Tech Events** (Eventbrite/Meetup proxy) | AI/tech conference calendar | Scrape | ❌ No | Daily |

**🎯 What this adds:**
- arXiv paper monitoring — new model releases (DeepSeek, Llama, etc.) hit arXiv before news
- HackerNews signal — community reaction to AI developments
- Trending GitHub repos — early signal for new AI tools/frameworks

---

### 🏥 HEALTH

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **NASA EONET** | Disease outbreak-linked events (floods → cholera, etc.) | EONET API | ❌ No | 1h |
| **GDACS** | Disaster alerts with humanitarian impact (linked to disease risk) | `https://www.gdacs.org/gdacsapi/` | ❌ No | 1h |
| **ACLED** | Violence against civilians near healthcare facilities | ACLED | ✅ Free | 15 min |
| **FRED** | Health expenditure indicators, pharmaceutical price indices | FRED | ✅ Free | Annual |
| **RSS: WHO/Reuters Health/STAT News** | Health news, outbreak alerts | RSS | ❌ No | 15 min |
| **Displacement Summary** | UNHCR displacement data (refugee → public health crises) | UNHCR-linked | ❌ No | Weekly |

**🎯 What this adds:**
- Natural disaster → disease outbreak early warning (floods + displacement = cholera risk)
- WHO alert monitoring via RSS

---

### 🔍 CONSPIRACY / 📁 EPSTEIN / 🕵️ BLACK BUDGET

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **GDELT DOC** | Keyword search: "deep state", "whistleblower", "classified", "FOIA", "declassified" | GDELT API | ❌ No | 15 min |
| **FRED: USA Spending** | US federal discretionary spending, black budget proxies | USA Spending API (via FRED) | ❌ No | Annual |
| **RSS: The Intercept/ProPublica/Substack** | Investigative journalism feeds | RSS | ❌ No | 15 min |
| **arXiv** | Surveillance technology papers (`cs.CR` security, cryptography) | arXiv | ❌ No | 1h |
| **Cyber Threats (OTX/URLhaus)** | State-sponsored cyber operations (Five Eyes, GRU, APT groups) | OTX/URLhaus | ✅ Free | 2h |

**🎯 What this adds:**
- Government spending anomaly detection via USA Spending API
- State-sponsored cyber operation tracking (attribution to nation-state actors)

---

### 💼 QUANT / 📊 WESTEAST / 🌐 EMERGING MARKETS

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **Yahoo Finance** | Country stock indices: Nikkei, Shanghai, Hang Seng, FTSE, DAX, Bovespa | Yahoo Finance | ❌ No | Daily |
| **BIS** | Credit/GDP ratios by country, FX rates, policy rates | BIS SDMX | ❌ No | Monthly |
| **FRED** | EM sovereign yields, currency pairs (BRL, INR, TRY, ZAR) | FRED | ✅ Free | Daily |
| **WTO Trade Flows** | Bilateral trade flows — China↔ASEAN, US↔EU, etc. | WTO API | ✅ Free | Annual |
| **WTO Tariff Trends** | Applied MFN tariff rates by reporter/partner country | WTO API | ✅ Free | Annual |
| **WTO Trade Restrictions** | Sanction-linked trade barriers | WTO API | ✅ Free | Monthly |
| **World Bank** | GDP, inflation, poverty, FDI, population indicators | WB API | ❌ No | Annual |
| **Gulf FDI** (config) | UAE, Saudi, Qatar inbound FDI tracking | Internal config data | — | — |
| **Gulf Market Quotes** | TADAWUL (Saudi), ADX (UAE), DSM (Qatar) indices | Yahoo Finance tickers | ❌ No | Daily |
| **Finnhub** | Sector-level stock performance, earnings calendar | Finnhub | ✅ Free | Real-time |
| **ETF Flows** | EEM, VWO (emerging market ETFs) flows | Yahoo Finance | ❌ No | Daily |

**🎯 What this adds:**
- Actual bilateral trade flow numbers (e.g. US-China trade volume declining YoY)
- EM sovereign yield tracking (Turkey, Brazil stress signals)
- Gulf stock market integration for Macro domain

---

### ✊ CULTURE / 🏆 SPORTS

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **ACLED** | Protest events (cultural/political) with location | ACLED | ✅ Free | 15 min |
| **GDELT DOC** | Cultural event keyword search | GDELT | ❌ No | 15 min |
| **RSS: Entertainment/Sports feeds** | Oscars, Grammy, NFL, NBA, Premier League | RSS | ❌ No | 15 min |
| **Positive Events** | Conservation wins, scientific breakthroughs, diplomatic progress | EONET + GDELT | ❌ No | 1h |

---

### ✝️ RELIGION

| API | Data | Endpoint | Key? | Update freq |
|---|---|---|---|---|
| **ACLED** | Religious violence events — filtered by `sub_event_type` | ACLED | ✅ Free | 15 min |
| **GDELT DOC** | Religious conflict keyword search (jihad, crusade, persecution, blasphemy) | GDELT | ❌ No | 15 min |
| **OREF Sirens** | Israeli missile alerts — linked to religious-nationalist conflict | OREF | ❌ No | Real-time |
| **RSS: Al Jazeera/Vatican News/Times of Israel** | Religion-linked news coverage | RSS | ❌ No | 15 min |

---

## Exclusive High-Value APIs (Not Currently in Intel Swarm)

These are the most impactful new integrations to consider:

### 🔴 Priority 1 — Build Now

| API | What it unlocks | Free? |
|---|---|---|
| **ACLED** | Real battlefield events with exact coords → real conflict map data | ✅ Free (register) |
| **FRED** | Yield curve, Fed policy, inflation — powers Macro + Quant domains | ✅ Free |
| **CoinGecko** | Live crypto prices with sparkline → Terminal page | ✅ Free |
| **Yahoo Finance** | Commodity futures, country indices, ETF flows | ✅ Free (no key) |
| **arXiv** | AI paper monitoring — DeepSeek/Llama papers hit here before news | ✅ Free |
| **Alternative.me** | Fear & Greed Index — single API call, massive signal value | ✅ Free |
| **OREF** | Israeli missile sirens → real-time war alerts | ✅ Free |

### 🟡 Priority 2 — Register & Integrate

| API | What it unlocks | Registration |
|---|---|---|
| **GDELT GEO (fix)** | Heat map with proper event coordinates (not CSV actor codes) | ❌ No key |
| **NASA FIRMS** | Active fire detections → war-linked arson, infrastructure fires | ✅ Free at earthdata.nasa.gov |
| **USGS Earthquakes** | Seismic events → mining/infrastructure disruption signal | ❌ No key |
| **NASA EONET** | Open natural events: storms, floods, volcanic eruptions | ❌ No key |
| **Cloudflare Radar** | Internet outages by country → digital warfare, censorship signal | ✅ Free at dash.cloudflare.com |
| **OTX AlienVault** | Cyber threat indicators — nation-state APT groups | ✅ Free at otx.alienvault.com |
| **WTO API** | Tariff rates, trade barriers — macro/westeast | ✅ Free at api.wto.org |
| **BIS SDMX** | Central bank policy rates — macro/quant | ❌ No key |
| **World Bank** | EM economic indicators | ❌ No key |
| **Finnhub** | Stock data, earnings — quant/macro | ✅ Free at finnhub.io |

### 🟢 Priority 3 — Premium When Ready

| API | What it unlocks | Cost |
|---|---|---|
| **ACLED full access** | 10-year conflict history, all event types | Free with research registration |
| **OpenSky** | Military flight tracking globally | Free (account for higher rate limits) |
| **EIA** | US energy data (oil, gas, power grid) | ✅ Free at eia.gov |
| **Finnhub** | Real-time stock quotes | Free tier + paid for real-time |
| **Groq** | Ultra-fast LLM inference for classification | Free tier |

---

## LLM Architecture (World Monitor Pattern)

World Monitor uses a 3-tier LLM fallback chain worth adopting:

```
1. Groq (llama-3.1-8b-instant) — fastest, cheapest, good enough for classification
2. Ollama (local model) — when Groq fails or for sensitive data
3. OpenRouter → Claude/GPT-4 — heavy reasoning tasks only
```

**Use cases in World Monitor:**
- `classify-event.ts` — classify a news event as CONFLICT/PROTEST/POLITICAL/NATURAL
- `deduct-situation.ts` — multi-source "what's really happening" synthesis
- `get-country-intel-brief.ts` — per-country LLM-generated intel brief
- `summarize-article.ts` — article summarization pipeline
- `search-gdelt-documents.ts` — semantic search over GDELT results

**→ For Intel Swarm:** this pattern maps directly to our researcher pipeline. Could replace or augment the current Sonnet-based researchers with Groq for speed + cost reduction, reserving Opus for the chief synthesis.

---

## Scraping Methods Used

| Method | Used For | Notes |
|---|---|---|
| **RSS parsing** | 100+ news feeds across all domains | curated in `_feeds.ts`, 8 categories |
| **Yahoo Finance scrape** | Commodities, ETF flows, macro signals, country indices | Uses `yahooGate()` sequential rate-limiter to avoid 429 |
| **OpenSky ADS-B** | Military flight detection | Filters by callsign pattern + hex code database |
| **OREF scrape** | Israeli missile sirens | Direct HTML scrape of oref.org.il |
| **GDELT CSV download** | Conflict events with lat/lng | `lastupdate.txt` → ZIP → CSV pipeline |
| **GPS Jam scrape** | GPS interference zones (spoofing/jamming) | `gpsjam.org` data |
| **USNI scrape** | US naval fleet report | Navy Institute News scrape |
| **Wingbits relay** | ADS-B backup when OpenSky is down | WebSocket relay |

---

## RSS Feeds Catalogue (World Monitor `_feeds.ts`)

100+ feeds across 8 categories — immediately usable in Intel Swarm:

**Politics/World:** BBC World, Guardian, AP, Reuters, CNN, France24, EuroNews, Le Monde, DW, Al Jazeera, BBC Middle East, Oman Observer

**US:** NPR, PBS NewsHour, ABC, CBS, NBC, WSJ, Politico, The Hill, Axios

**Tech:** Hacker News, Ars Technica, The Verge, MIT Tech Review

**AI:** VentureBeat AI, The Verge AI, MIT Tech Review AI, ArXiv cs.AI

**Finance:** CNBC, MarketWatch, Yahoo Finance, FT, Bloomberg RSS proxy

**Science:** Nature, Science AAAS, New Scientist, Scientific American

**Crypto:** CoinDesk, CoinTelegraph, The Block, Decrypt

**Military/Defense:** War on the Rocks, Defense One, USNI News, Bellingcat

---

## Recommended Integration Roadmap

### Phase 1 (This Week) — Zero Cost, No New Keys
1. **CoinGecko** → Live crypto prices on Terminal + Crypto domain
2. **Yahoo Finance** → Commodity futures + country stock indices + ETF flows
3. **arXiv cs.AI** → Real-time AI paper monitoring for AI Agents domain
4. **Alternative.me Fear & Greed** → Single metric, massive macro signal
5. **BIS SDMX** → Central bank policy rates for Macro domain
6. **USGS** → Earthquake feed for Conflict Map + Black Budget domain
7. **NASA EONET** → Natural events feed

### Phase 2 (Register for Free Keys)
1. **ACLED** → Replace fake GDELT actor codes with real conflict events on Conflict Map
2. **FRED** → Full macro data layer (yield curve, CPI, M2 money supply)
3. **NASA FIRMS** → Wildfire/active fire detections
4. **Cloudflare Radar** → Internet outage monitoring (BlackBudget/War domains)
5. **OTX AlienVault** → Cyber threat intel for BlackBudget domain
6. **Finnhub** → Stock quotes for Quant domain
7. **EIA** → Energy data for Commodities domain
8. **WTO** → Tariff/trade data for WestEast + Macro

### Phase 3 (Infrastructure)
1. **Groq LLM** → Fast classifier for breaking news event typing
2. **OpenSky** → Military flight tracking on Conflict Map
3. **OREF** → Israeli missile siren real-time alerts
4. **GPS Jam** → GPS spoofing zones (military activity signal)
5. **USNI** → US fleet posture reporting

---

*Generated by CD (Intel Swarm) — full scan of `koala73/worldmonitor` commit history and server module directory. Last updated: 2026-03-05.*
