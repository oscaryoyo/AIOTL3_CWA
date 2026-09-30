# 🌦️ 台灣即時氣象地圖 Taiwan Weather Map

> **AI 創新微課程：從氣象資料到互動式天氣預報應用**  
> *用程式探索天氣 · 用資料看見台灣 · 用 AI 實現更多可能*  
> *Code Smarter, Build a Better Tomorrow!*

---

> 「技術可以解決問題，但更重要的是用技術創造更好的未來！」—— 煥哥

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=flat&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-Maps-199900?style=flat&logo=leaflet&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?style=flat&logo=chart.js&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Live-000000?style=flat&logo=vercel&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

---

## 🔗 Quick Links

| 類型 | 連結 |
| :--- | :--- |
| 🌐 **線上網站 (Vercel Live)** | **[https://aiotl-3-cwa.vercel.app/](https://aiotl-3-cwa.vercel.app/)** |
| 📦 **GitHub Repository** | [https://github.com/oscaryoyo/AIOTL3_CWA](https://github.com/oscaryoyo/AIOTL3_CWA) |
| 📡 **CWA Open Data API** | [https://opendata.cwa.gov.tw/](https://opendata.cwa.gov.tw/) |
| 💻 **本機開發網址** | [http://127.0.0.1:5000](http://127.0.0.1:5000)（需先執行 `python app.py`）|

---

## 📌 專案簡介 (Project Overview)

本專案為 **AI 創新微課程** 之實戰作品。透過串接**交通部中央氣象署（CWA）Open Data API**，即時取得台灣 22 縣市最新氣象預測數據（氣溫、降雨機率、風向風速、溫濕度體感、天氣現象），並整合颱風路徑、觀測站資料，以全螢幕互動地圖呈現。

前端採用 **Leaflet.js** 地圖搭配**台灣行政區 GeoJSON**，實現真實縣市邊界的**連續色階 Choropleth 地圖**（每 1°C 對應唯一色彩），並支援直接部署至 **Vercel** 無伺服器雲端平台。

---

## ✨ 功能特色 (Features)

### 🗺️ 全螢幕互動式氣象地圖
- **真實台灣行政區邊界 Choropleth** — 從 GitHub 動態載入 GeoJSON，以縣市真實多邊形呈現各縣市氣象資訊
- **5 種氣象模式切換**（頂部選單列）：
  | 模式 | 圖示 | 說明 |
  |------|------|------|
  | 🌡️ 氣溫 | 連續色階 | 每 1°C 對應唯一顏色（深藍 → 淺藍 → 黃 → 橙 → 深紅） |
  | 🌧️ 降雨機率 | 連續色階 | 0~100% 對應白 → 淺藍 → 深藍 → 靛紫 |
  | 💨 風向風速 | 泡泡標記 | 箭頭方向＋m/s 數值 |
  | 💧 溫濕度體感 | 泡泡標記 | 相對濕度 % |
  | ⛅ 天氣現象 | 泡泡標記 | 圖示＋天氣描述 |

### 🎨 平滑色彩插值引擎
- **氣溫色階**：15°C（深藍）→ 21°C（淺青）→ 25°C（綠）→ 27°C（黃）→ 31°C（橙）→ 35°C（紅）→ 38°C（暗紅）— RGB 線性插值，無階梯感
- **降雨色階**：0%（近白）→ 40%（天藍）→ 70%（深藍）→ 100%（深紫）
- **氣溫橙色膠囊標籤**：各縣市顯示當前氣溫值，顏色匹配色階，懸停有放大動畫

### 🌀 颱風路徑追蹤
- 歷史路徑（紅色實線）＋預測路徑（橙色虛線）
- 每個節點顯示**永久時間標籤**（格式：`MM-DD HH:MM`）
- 點擊節點顯示風速、氣壓、移動方向詳情
- 70% 暴風機率半徑圈

### 📍 氣象觀測站點
- 以藍色圓點標示全台觀測站位置
- 點擊顯示即時氣溫、濕度、風速、雨量

### 📊 縣市預報走勢小視窗
- 可拖曳的浮動報表視窗（左側），包含：
  - 2×2 KPI 指標卡（最高/最低溫、天氣狀況、降雨風速）
  - **Chart.js 折線圖**（7 天最高/最低溫趨勢）
  - 預報明細表格（日期、氣溫、天氣、降雨、舒適度）
- 頂部下拉選單可快速切換縣市

### 🗺️ 多樣底圖
| 底圖 | 說明 |
|------|------|
| 🌑 極客深色 | Esri Dark Gray（預設，最適合氣象視覺化）|
| 🛰️ 衛星影像 | Esri World Imagery |
| 🗺️ 街道圖 | OpenStreetMap |

### ⏱️ 資料更新
- 頁面頂端顯示**最後資料更新時間**
- **「同步 CWA 最新數據」**按鈕：呼叫 `/api/sync`，即時觸發 ETL 並重新整理頁面

---

## 🛠️ 核心技術棧 (Tech Stack)

| 領域 | 技術 & 工具 | 說明 |
| :--- | :--- | :--- |
| **資料來源** | [CWA Open Data API](https://opendata.cwa.gov.tw/) | 縣市預報、觀測站、颱風路徑 |
| **程式語言** | Python 3.9+ | 後端核心 |
| **Web 框架** | Flask 3.0+ | Serverless Function (Vercel) |
| **資料分析** | Pandas | JSON 攤平、DataFrame 清洗 |
| **資料庫** | SQLite3 | 縣市預報資料持久化，Vercel 環境寫入 `/tmp` |
| **地圖** | Leaflet.js 1.9 + GeoJSON | Choropleth、颱風路徑、觀測站點 |
| **圖表** | Chart.js 4.4 | 7 天溫度折線圖 |
| **字型** | Google Fonts (Noto Sans TC + Outfit) | 中英文優化排版 |
| **部署** | Vercel Serverless | 自動 CI/CD from GitHub |
| **版本控制** | Git / GitHub | 版控與開源協作 |

---

## 🏗️ 系統架構 (System Architecture)

```mermaid
flowchart TD
    subgraph CWA["🌐 CWA Open Data API"]
        A1[縣市天氣預報\nF-C0032-001]
        A2[自動氣象站觀測\nO-A0001-001]
        A3[颱風路徑資料\nW-C0034-005]
    end

    subgraph ETL["🔄 ETL Pipeline (fetch_data.py)"]
        B1[cwa_service.py\n取得原始 JSON]
        B2[data_processor.py\nPandas 清洗 / 解析]
        B3[database.py\nSQLite Upsert]
        B4[JSON Cache\ntyphoon / stations]
    end

    subgraph Flask["⚙️ Flask App (app.py)"]
        C1[/ 主頁面]
        C2[/api/weather]
        C3[/api/typhoon]
        C4[/api/stations]
        C5[/api/sync]
    end

    subgraph Frontend["🖥️ 前端 (index.html)"]
        D1[Leaflet 地圖]
        D2[GeoJSON Choropleth\n平滑色彩插值]
        D3[Chart.js 折線圖]
        D4[颱風路徑 + 時間標籤]
        D5[觀測站點]
    end

    CWA --> ETL
    ETL --> Flask
    Flask --> |Jinja2 Template| Frontend
    Frontend --> |fetch| Flask
```

---

## 📁 專案結構 (Project Structure)

```
AIOTL3_CWA/
├── app.py                  # Flask 主程式 (路由、Vercel 相容處理)
├── fetch_data.py           # ETL Pipeline 入口 (抓取 → 解析 → 入庫)
├── cwa_service.py          # CWA API 呼叫模組 (預報 / 觀測站 / 颱風)
├── data_processor.py       # Pandas 資料清洗與解析邏輯
├── database.py             # SQLite CRUD 操作模組
├── templates/
│   └── index.html          # 全螢幕互動式氣象地圖主頁面 (Leaflet + Chart.js)
├── data.db                 # SQLite 資料庫 (縣市預報)
├── typhoon_cache.json      # 颱風路徑快取
├── stations_cache.json     # 觀測站位置快取
├── update_time.txt         # 最後更新時間戳記
├── vercel.json             # Vercel 部署設定
├── requirements.txt        # Python 套件清單
├── .env.example            # 環境變數範本
└── .gitignore
```

---

## 🗄️ 資料庫結構 (Database Schema)

```sql
CREATE TABLE IF NOT EXISTS TemperatureForecasts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    locationName    TEXT NOT NULL,   -- 縣市名稱 (如：臺北市、高雄市)
    dataDate        TEXT NOT NULL,   -- 預報日期 (YYYY-MM-DD)
    mint            REAL,            -- 最低氣溫 (°C)
    maxt            REAL,            -- 最高氣溫 (°C)
    wx              TEXT,            -- 天氣現象描述
    pop             TEXT,            -- 降雨機率 (%)
    ci              TEXT,            -- 舒適度指數
    windSpeed       REAL,            -- 風速 (m/s)
    windDirection   REAL,            -- 風向 (度)
    humidity        REAL,            -- 相對濕度 (%)
    precipitation   REAL,            -- 降水量 (mm)
    UNIQUE(locationName, dataDate)   -- 防止重複入庫
);
```

---

## 🚀 快速開始 (Quick Start)

### 1. 取得中央氣象署 API 授權碼
前往 [CWA Open Data Platform](https://opendata.cwa.gov.tw/)，註冊後取得 **API Authorization Key**。

### 2. 複製專案並安裝依賴
```bash
git clone https://github.com/oscaryoyo/AIOTL3_CWA.git
cd AIOTL3_CWA

# 建立虛擬環境（建議）
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 安裝套件
pip install -r requirements.txt
```

### 3. 設定環境變數
```bash
# 複製範本並填入 API Key
cp .env.example .env
```
編輯 `.env`：
```ini
CWA_API_KEY=CWA-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

### 4. 執行 ETL（抓取氣象資料並入庫）
```bash
python fetch_data.py
```

### 5. 啟動本機 Flask 伺服器
```bash
python app.py
```
開啟瀏覽器至 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🌐 Vercel 雲端部署 (Vercel Deployment)

本專案已全面支援 Vercel Serverless Python 部署：

1. **匯入 GitHub 倉庫**：登入 [Vercel](https://vercel.com/) → Add New Project → 選擇 `oscaryoyo/AIOTL3_CWA`
2. **設定環境變數**：
   | Key | Value |
   |-----|-------|
   | `CWA_API_KEY` | 您的中央氣象署 API 金鑰 |
3. **部署**：點擊 Deploy，Vercel 自動辨識 `vercel.json` 完成部署

> **Vercel 相容性說明**：Vercel 為唯讀 Serverless 環境，SQLite 資料庫與快取 JSON 自動複製至 `/tmp`（可寫目錄）。

### REST API 端點
| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | 主頁面（完整氣象地圖儀表板）|
| `/api/weather` | GET | 天氣預報資料（支援 `?city=臺北市`）|
| `/api/typhoon` | GET | 颱風路徑快取資料 |
| `/api/stations` | GET | 氣象觀測站位置資料 |
| `/api/sync` | GET/POST | 觸發 ETL 同步 CWA 最新資料 |

---

## 🗺️ 學習地圖與課程架構 (Course Curriculum)

```mermaid
flowchart LR
    A[Phase 1<br/>觀念與資料取得] --> B[Phase 2<br/>資料清洗與整理]
    B --> C[Phase 3<br/>資料庫設計]
    C --> D[Phase 4<br/>Web 互動入門]
    D --> E[Phase 5<br/>圖表與進階地圖]
    E --> F[Phase 6<br/>優化與雲端部署]
```

| 階段 | 單元 | 重點 |
|------|------|------|
| Phase 1 | 01-04 | CWA API 串接、requests、JSON 取得 |
| Phase 2 | 05-07 | JSON 解析、Pandas 清洗、氣溫萃取 |
| Phase 3 | 08-10 | SQLite 設計、CRUD、SQL 驗證 |
| Phase 4 | 11-13 | Flask 路由、Jinja2 模板、前端互動 |
| Phase 5 | 14-19 | Chart.js 折線圖、Leaflet 地圖、Choropleth |
| Phase 6 | 20-24 | 模組化、Git/GitHub、Vercel 部署、延伸應用 |

---

## 💡 延伸應用 (Future Roadmap)

- [ ] **天氣預警 LINE Bot**：每日自動推播今日氣溫與攜帶雨具提醒
- [ ] **旅遊休閒建議系統**：結合降雨機率與舒適度，智慧推薦出遊地點
- [ ] **智慧農業 / 防災監控**：連續低溫或強降雨自動發送緊急通報
- [ ] **生成式 AI 整合**：OpenAI / Gemini 自動生成口語化天氣播報與穿搭建議
- [ ] **歷史資料分析**：長期氣溫趨勢、極端氣候統計
- [ ] **PWA 行動版支援**：手機離線快取、推播通知

---

## 👨‍🏫 關於微課程 (About)

- **課程名稱**：AI 創新微課程 - Taiwan Weather Forecast
- **線上展示**：[https://aiotl-3-cwa.vercel.app/](https://aiotl-3-cwa.vercel.app/)
- **講師理念**：*「技術可以解決問題，但更重要的是用技術創造更好的未來！」—— 煥哥*
- **精神標語**：Learn Today, Build Tomorrow | AI for Learning, AI for a Better Taiwan
