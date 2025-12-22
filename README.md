# 🚀 專案計畫書：DebateAI

## 多 Agent 即時辯論與協作平台

---

## 📋 目

1. [專案概述](#1-專案概述)
2. [系統架構設計](#2-系統架構設計)
3. [功能詳細規格](#3-功能詳細規格)
4. [開發階段規劃](#4-開發階段規劃)
5. [部署與配置清單](#5-部署與配置清單)
6. [預期成果](#6-預期成果)
7. [實施狀態](#7-實施狀態)

---

## 1. 專案概述

### 1.1 專案簡介

**DebateAI** 是一個基於 **LangGraph** 的多 Agent 協作平台，展示 AI 如何針對特定主題進行結構化的辯論與事實查核。

### 1.2 核心特色

- ✅ **複雜的 Agent 狀態管理**
- ✅ **工具調用 (Tool Use)**
- ✅ **即時串流 (Streaming)**
- ✅ **全端開發整合**

### 1.3 核心價值

證明開發者具備以下能力：

- **Python (LangGraph/FastAPI)** 後端開發
- **Modern Frontend (Next.js)** 前端開發
- **LLM 推理速度優化 (Groq)** 實戰經驗

---

## 2. 系統架構設計

### 2.1 架構概述

採用 **前後端分離 (Decoupled Architecture)**，確保最佳的互動體驗與後端邏輯的可擴展性。

### 2.2 技術堆疊 (Tech Stack)

| 領域               | 技術選型                     | 詳細說明 / 部署策略                                                                                                                                                                                                                                                           |
| :----------------- | :--------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Python 工具鏈**  | **uv**                       | • 現代化依賴管理（比 pip 快 10-100 倍）<br>• 內建依賴鎖定（uv.lock）<br>• 統一工具鏈                                                                                                                                                                                          |
| **前端 Framework** | **Next.js 14+**              | • 使用 App Router<br>• 部署於 **Cloudflare Pages**<br>• 使用 `output: 'export'` 靜態導出<br>• Phase 1 用 `EventSource` (GET)<br>• Phase 2+ 用 `fetch + ReadableStream` (POST)                                                                                                 |
| **後端 Framework** | **FastAPI**                  | • Python 3.11+<br>• 部署於 **Google Cloud Run** (Docker Container)<br>• 使用 **uv** 管理依賴<br>• 提供 SSE 串流接口（私有部署）                                                                                                                                               |
| **AI 框架**        | **LangGraph v1**             | • v1 是穩定釋出，核心 graph API/執行模型維持不變<br>• 使用 `astream_events`/`stream` 串流，checkpointing 與 persistence 一級公民<br>• 官方已將 `create_react_agent` 標示 deprecated，建議改用 LangChain `create_agent`（底層仍是 LangGraph）                                  |
| **LLM 核心**       | **Groq**                     | • Llama-3.1-70b 模型<br>• 利用 Groq 的 LPU 提供每秒 300+ token 的超快推理<br>• 使用 streaming 模式實現打字機效果                                                                                                                                                              |
| **搜尋工具**       | **Tavily + DuckDuckGo Text** | • **Tavily**：專為 AI 設計，伺服器端完成內容清洗（1000 次/月免費）<br>• **DuckDuckGo**：文字摘要搜尋，完全免費備援<br>• **三層容錯**：Tavily → DDGS Text → 優雅降級<br>• **回應速度**：< 1 秒，適合即時辯論<br>• **Phase 4 可選**：Playwright 深度爬取（獨立 Cloud Function） |
| **通訊協定**       | **HTTP + SSE**               | • Phase 1: GET + EventSource (簡單測試)<br>• Phase 2+: POST + fetch + ReadableStream (完整功能)                                                                                                                                                                               |

> ⚠️ **戰略警語：先保辯論節奏，再談深爬**  
> Phase 1-3 僅使用 Tavily/DDGS 文字搜尋，確保 <1 秒開始串流；Playwright 視為 Phase 4 的「深度查證」外掛，應獨立部署（Cloud Functions/獨立容器）後再由主流程呼叫，避免拖慢 Cloud Run 冷啟動與記憶體。

### 2.3 架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                     使用者瀏覽器                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Next.js Frontend (Cloudflare Pages)           │  │
│  │  • React Components                                   │  │
│  │  • SSE Client (EventSource / fetch)                   │  │
│  │  • Real-time UI Updates                               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │ HTTPS + SSE
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Google Cloud Run)             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  LangGraph Workflow                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │  Optimist   │  │  Skeptic    │  │  Moderator  │  │  │
│  │  │   Agent     │  │   Agent     │  │   (Phase 2) │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │         │                │                │          │  │
│  │         └────────────────┴────────────────┘          │  │
│  │                         │                            │  │
│  │                    StateGraph                        │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              External Services                        │  │
│  │  • Groq API (LLM)                                     │  │
│  │  • Tavily Search                                      │  │
│  │  • DuckDuckGo Search (Fallback)                       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 功能詳細規格

### 3.1 LangGraph 流程設計

#### 3.1.1 狀態定義 (State Schema)

```python
from typing import Annotated, Literal, List, TypedDict
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class DebateState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]  # 自動累積訊息
    topic: str                                             # 辯論主題
    current_speaker: Literal["optimist", "skeptic", "end"] # 下一位發言者
    round_count: int                                       # 當前輪數
    max_rounds: int                                        # 最大輪數
```

#### 3.1.2 Agent 節點與角色

##### 1. Optimist (樂觀者)

- **職責**：從積極角度論述
- **工具**：若論點需要數據，自動調用 `web_search`
- **特色**：強調機會、優勢與正面影響

##### 2. Skeptic (懷疑者)

- **職責**：找出對方邏輯漏洞，強調風險
- **工具**：若發現對方數據可疑，調用 `web_search` 進行查核
- **特色**：批判性思考、風險評估

##### 3. Moderator (主持人 - Phase 2)

- **職責**：當 `round_count` 達到上限時觸發
- **功能**：閱讀歷史並生成總結報告
- **輸出**：平衡的結論與關鍵洞察

### 3.2 即時串流機制

#### 3.2.1 技術實現

**為什麼需要串流？**
解決 LLM 響應延遲的問題，提供更好的用戶體驗。

**實現方式：**

1. **Backend (LangGraph 1.0)**

   ```python
   # 使用 astream() + stream_mode="messages"
   async for message, metadata in graph.astream(
       state,
       stream_mode="messages"
   ):
       # 捕捉每個 token
       if hasattr(message, 'content') and message.content:
           node = metadata.get("langgraph_node", "unknown")
           yield {"node": node, "text": message.content}
   ```

2. **Transport (SSE)**

   ```python
   # FastAPI SSE 格式
   async def stream_debate():
       async for chunk in langraph_stream():
           yield f"data: {json.dumps(chunk)}\n\n"
   ```

3. **Frontend (React)**
   ```typescript
   // EventSource 連接
   const eventSource = new EventSource("/api/debate/stream");
   eventSource.onmessage = (event) => {
     const data = JSON.parse(event.data);
     // 根據 node 渲染到對應位置
     updateUI(data.node, data.text);
   };
   ```

#### 3.2.2 用戶體驗

- ✅ **打字機效果**：逐字顯示，提升互動感
- ✅ **即時反饋**：無需等待完整回應
- ✅ **角色區分**：不同 Agent 顯示在不同區域
- ✅ **狀態指示**：顯示「正在思考...」、「正在搜尋...」

---

## 4. 開發階段規劃

### 🔴 Phase 1: 基礎架構連通

**目標**：確保 Cloudflare 前端能連上 Cloud Run 後端，並看到字在動。

#### 後端任務

- [ ] 建立 FastAPI 專案，撰寫 `Dockerfile`（使用 uv）
- [ ] 實作 Fake SSE 接口（每秒回傳 "Hello" → "World"）
- [ ] 配置 `CORSMiddleware`（從環境變數 `ALLOWED_ORIGINS` 讀取）
- [ ] 部署至 **Google Cloud Run**（私有模式，使用 API Key 驗證）

#### 前端任務

- [ ] 建立 Next.js 介面
- [ ] 使用 `EventSource` 連接後端 URL
- [ ] 部署至 **Cloudflare Pages**
- [ ] 記下實際 URL 並更新後端 CORS 配置

#### 驗收標準

✅ 前端能看到後端推送的測試訊息
✅ CORS 配置正確，無跨域錯誤
✅ 部署環境正常運作

---

### 🟡 Phase 2: 接入 LangGraph 與 Groq

**目標**：真正的 AI 辯論，Agent 能夠針對主題對話。

#### 後端任務

- [ ] 申請 **Groq API Key** 並寫入 Cloud Run 環境變數
- [ ] 實作 `Optimist` 與 `Skeptic` 的 LangGraph 節點
- [ ] 將 `astream_events` 串接到 FastAPI 的 `StreamingResponse`
- [ ] 實作狀態管理邏輯（輪次控制、發言順序）

#### 前端任務

- [ ] 優化 UI，根據 Agent 角色顯示不同顏色的對話氣泡
- [ ] 實作主題輸入表單
- [ ] 添加輪次設定功能
- [ ] 實作載入狀態與錯誤處理

#### 驗收標準

✅ 輸入主題後，兩個 Agent 開始辯論
✅ 即時串流顯示正常
✅ 辯論能自動結束

---

### 🟢 Phase 3: 工具調用與完善

**目標**：加入聯網能力，讓辯論言之有物。

> ⚠️ 本階段只整合 Tavily/DDGS 文字搜尋，不引入 Playwright；若需深度爬取，留待 Phase 4 以獨立外掛服務方式接入。

#### 後端任務

- [ ] 整合 **Tavily（主）+ DuckDuckGo（備援）** 三層容錯搜尋工具
- [ ] 在 LangGraph 中加入 `bind_tools`
- [ ] 使用 `ToolMessage` 保持訊息鏈完整性
- [ ] 在 SSE 中加入 `on_tool_start` 和 `on_tool_end` 事件監聽
- [ ] 實作 Moderator 節點（總結報告）

#### 前端任務

- [ ] 在 UI 上顯示「Agent 正在搜尋中...」的狀態指示器
- [ ] 實作搜尋結果來源顯示
- [ ] 添加總結報告展示區
- [ ] 優化整體 UI/UX

#### 驗收標準

✅ Agent 能自動調用搜尋工具
✅ 搜尋狀態在 UI 上清晰顯示
✅ 辯論結束後顯示總結報告
✅ 三層容錯機制正常運作

---

## 5. 部署與配置清單

### 5.1 Google Cloud Run (Backend)

#### 專案結構

```
backend/
├── pyproject.toml          # uv 依賴配置
├── uv.lock                 # 依賴鎖定檔
├── Dockerfile              # 容器化配置
├── app/
│   ├── main.py            # FastAPI 應用
│   ├── graph.py           # LangGraph 定義
│   ├── agents/            # Agent 節點
│   │   ├── optimist.py
│   │   ├── skeptic.py
│   │   └── moderator.py
│   └── tools/             # 搜尋工具
│       ├── tavily.py
│       └── duckduckgo.py
└── .env.example           # 環境變數範例
```

#### pyproject.toml

```toml
[project]
name = "debate-ai-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "langchain>=0.3.0",
    "langchain-groq>=0.2.0",
    "langgraph>=0.2.0",
    "tavily-python>=0.5.0",
    "duckduckgo-search>=6.0.0",
    "python-dotenv>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### Dockerfile (使用 uv)

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# 複製依賴定義
COPY pyproject.toml uv.lock* ./

# 安裝依賴（生產環境）
RUN uv sync --frozen --no-dev

# 複製應用程式碼
COPY app ./app

# 暴露端口
EXPOSE 8080

# 啟動應用
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### 部署指令

```bash
# 私有部署（推薦）
gcloud run deploy debate-api \
  --source . \
  --region asia-east1 \
  --set-env-vars GROQ_API_KEY=${GROQ_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY} \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10

# 取得服務 URL
gcloud run services describe debate-api \
  --region asia-east1 \
  --format 'value(status.url)'
```

#### 環境變數

| 變數名稱          | 說明                        | 範例                          |
| :---------------- | :-------------------------- | :---------------------------- |
| `GROQ_API_KEY`    | Groq API 金鑰               | `gsk_xxxx...`                 |
| `TAVILY_API_KEY`  | Tavily API 金鑰             | `tvly-xxxx...`                |
| `API_SECRET_KEY`  | 簡單 API Key 驗證           | `your-secret-key`             |
| `ALLOWED_ORIGINS` | CORS 允許的來源（逗號分隔） | `https://debate-ai.pages.dev` |

#### CORS 配置 (main.py)

```python
import os
from fastapi.middleware.cors import CORSMiddleware

# ⚠️ 重要：不支援 *.pages.dev 通配符
# 必須填入實際的完整域名
ALLOWED_ORIGINS = [
    "http://localhost:3000",                      # 本地開發
    "https://debate-ai-abc123.pages.dev",         # Cloudflare Pages
    # 如有多個部署環境，逐一列出
]

# 或從環境變數讀取（推薦）
if os.getenv("ALLOWED_ORIGINS"):
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True,
)
```

---

### 5.2 Cloudflare Pages (Frontend)

#### 專案結構

```
frontend/
├── package.json
├── next.config.js          # 配置 output: 'export'
├── .env.example            # 環境變數範例
├── app/
│   ├── layout.tsx
│   ├── page.tsx           # 主頁面
│   └── components/
│       ├── DebateUI.tsx   # 辯論介面
│       ├── ChatBubble.tsx # 對話氣泡
│       └── TopicForm.tsx  # 主題輸入表單
└── lib/
    └── api.ts             # API 調用邏輯
```

#### next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export", // 靜態導出
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;
```

#### 環境變數

**開發環境 (`.env.local`)**

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**生產環境 (Cloudflare Pages 設定)**

```bash
# 選項 1: 使用 Cloudflare Workers 代理（推薦）
NEXT_PUBLIC_API_URL=https://debate-ai.yourdomain.workers.dev

# 選項 2: 直連 Cloud Run（需處理認證）
NEXT_PUBLIC_API_URL=https://debate-api-xxx.run.app
```

#### 前端存取策略

**選項 1: Cloudflare Workers 代理（推薦）**

```javascript
// workers/api-proxy.js
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const backendUrl = `https://debate-api-xxx.run.app${url.pathname}`;

    const headers = new Headers(request.headers);
    headers.set("Authorization", `Bearer ${env.API_SECRET_KEY}`);

    return fetch(backendUrl, {
      method: request.method,
      headers: headers,
      body: request.body,
    });
  },
};
```

**選項 2: Cloud Run 內建認證**

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL;
const ID_TOKEN = process.env.NEXT_PUBLIC_ID_TOKEN;

export async function streamDebate(topic: string) {
  const eventSource = new EventSource(
    `${API_URL}/debate/stream?topic=${encodeURIComponent(topic)}`,
    {
      headers: {
        Authorization: `Bearer ${ID_TOKEN}`,
      },
    }
  );
  return eventSource;
}
```

#### 部署步驟

```bash
# 1. 安裝依賴
npm install

# 2. 本地測試
npm run dev

# 3. 構建靜態檔案
npm run build

# 4. 部署到 Cloudflare Pages
# 方法 A: 透過 Git 自動部署（推薦）
git push origin main

# 方法 B: 使用 Wrangler CLI
npx wrangler pages deploy out
```

#### 取得 Cloudflare Pages 網址

```bash
# 部署後會顯示，格式為：
# https://[專案名稱]-[分支]-[隨機字串].pages.dev
# 例如：https://debate-ai-main-abc.pages.dev

# 或綁定自定義域名
# 例如：https://debate.yourdomain.com
```

---

### 5.3 搜尋工具配置

#### Tavily（主要）

```python
# app/tools/tavily.py
from tavily import TavilyClient
import os

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

async def tavily_search(query: str) -> dict:
    try:
        results = tavily_client.search(
            query=query,
            max_results=3,
            search_depth="basic"
        )
        return {
            "success": True,
            "results": results["results"],
            "source": "tavily"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "source": "tavily"
        }
```

#### DuckDuckGo（備援）

```python
# app/tools/duckduckgo.py
from duckduckgo_search import DDGS

async def duckduckgo_search(query: str) -> dict:
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=3))
        return {
            "success": True,
            "results": results,
            "source": "duckduckgo"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "source": "duckduckgo"
        }
```

#### 三層容錯策略

```python
# app/tools/search.py
async def web_search(query: str) -> dict:
    # 第一層：嘗試 Tavily
    result = await tavily_search(query)
    if result["success"]:
        return result

    # 第二層：嘗試 DuckDuckGo
    result = await duckduckgo_search(query)
    if result["success"]:
        return result

    # 第三層：優雅降級
    return {
        "success": False,
        "message": "搜尋服務暫時無法使用，Agent 將基於現有知識繼續辯論。",
        "source": "fallback"
    }
```

---

## 6. 預期成果

完成此計畫後，你將擁有：

### 6.1 技術展示

✅ **高效能的 AI 應用**

- 透過 Groq 實現近乎零延遲的 AI 回應
- Token-level streaming 提供流暢的用戶體驗

✅ **低成本/免費的架構**

- 善用 Cloud Run 免費額度
- Cloudflare 靜態託管完全免費
- Tavily 每月 1000 次免費查詢

✅ **完整的技術棧整合**

- **Multi-Agent Workflow**：LangGraph 狀態管理
- **Tool Use**：動態搜尋與事實查核
- **Streaming**：即時互動體驗

### 6.2 可展示的功能

1. **即時 AI 辯論**

   - 輸入主題，觀看兩個 Agent 即時對話
   - 每個字逐一顯示，提升互動感

2. **智能搜尋整合**

   - Agent 自動判斷是否需要搜尋
   - 搜尋結果融入論述
   - 三層容錯確保穩定性

3. **專業的總結報告**
   - Moderator 分析整場辯論
   - 提供平衡的結論與洞察

### 6.3 展示重點

當向面試官或同行展示時，強調：

- 🎯 **架構設計能力**：前後端分離、容器化部署
- 🤖 **AI 工程實力**：LangGraph multi-agent、工具調用
- ⚡ **性能優化經驗**：Groq LPU、串流技術
- 💰 **成本意識**：零成本實現企業級功能
- 🛡️ **穩定性思維**：三層容錯、優雅降級

---

## 7. 實施狀態

### 7.1 當前階段

**✅ Phase 1 完成，已部署到生產環境**

| 服務 | 平台             | URL                                                 |
| ---- | ---------------- | --------------------------------------------------- |
| 前端 | Cloudflare Pages | https://debateai.roy422.ggff.net                    |
| 後端 | Cloud Run        | https://debate-api-1046434677262.asia-east1.run.app |

### 7.2 最新更新（2025-12-05）

#### ✅ Phase 1 完成事項

- **前端**：Next.js 16 + shadcn/ui 組件整合，部署到 Cloudflare Pages
- **後端**：FastAPI + Fake SSE 串流，部署到 Cloud Run
- **CORS**：支援 `*.pages.dev` + `*.ggff.net` 自訂網域
- **部署自動化**：`deploy.sh` 一鍵部署腳本

#### 🚧 Phase 2 進行中

- 接入 LangGraph + Groq API
- 實作真實的 AI 辯論邏輯

### 7.3 技術棧優化（2025-12-04）

#### ✅ 技術棧優化

- **採用 uv 全家桶**：現代化 Python 工具鏈（比 pip 快 10-100 倍）
- **LangGraph v1**：穩定釋出，核心 API 不變；使用 `astream_events`/`stream` 串流，`create_react_agent` 已 deprecated，優先改用 LangChain `create_agent`
- **Tavily 優先搜尋**：三層容錯策略（Tavily → DuckDuckGo → 優雅降級）

#### ✅ 架構改進

- **冷啟動優化**：前端 UX 改善 + Demo Keep-Alive 腳本
- **零成本架構**：完整的免費方案實施指南
- **安全性強化**：私有部署 + API Key 驗證

### 7.3 技術堆疊摘要

| 組件              | 技術                   | 版本          | 說明                       |
| :---------------- | :--------------------- | :------------ | :------------------------- |
| **Python 工具鏈** | uv                     | latest        | 現代化依賴管理             |
| **後端框架**      | FastAPI                | 0.115+        | 高效能 async API           |
| **AI 框架**       | LangGraph              | 1.0+          | 最新穩定版 multi-agent API |
| **LLM**           | Groq                   | Llama-3.1-70b | 超快推理速度               |
| **搜尋工具**      | Tavily + DuckDuckGo    | -             | 三層容錯                   |
| **前端**          | Next.js                | 14+           | App Router                 |
| **部署**          | Cloud Run + Cloudflare | -             | 零成本方案                 |

### 7.4 快速開始

#### 步驟 1：安裝 uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 步驟 2：參閱完整實施文檔

詳細的實施指南請參閱：**[IMPLEMENTATION.md](./IMPLEMENTATION.md)**

包含內容：

- ✅ 可行性評估（9/10 高度可行）
- 📋 完整的 Phase 0-3 實施步驟
- 💻 完整程式碼範例
- 🚀 部署指南
- 🛡️ 風險緩解策略
- 💰 零成本架構清單

#### 步驟 3：開始 Phase 0（專案初始化）

```bash
# 後端初始化
mkdir debate-ai-backend && cd debate-ai-backend
uv init
uv add fastapi uvicorn langchain langchain-groq langgraph

# 前端初始化
npx create-next-app@latest debate-ai-frontend
cd debate-ai-frontend
npm install
```

### 7.5 預期時程

| 階段       | 時間   | 內容                      |
| :--------- | :----- | :------------------------ |
| **Week 1** | 5-7 天 | 基礎建設 + 學習 LangGraph |
| **Week 2** | 5-7 天 | 核心 AI 辯論功能          |
| **Week 3** | 5-7 天 | 搜尋工具整合              |
| **Week 4** | 3-5 天 | 完善與展示準備            |

**總計**：約 1 個月完成 MVP + 進階功能

### 7.6 進階功能規劃（Phase 4+）

#### 🎯 觀賞性增強（Entertainment Features）

##### 1. 戰況拉鋸條（Tug-of-War Bar）
- **目標**：視覺化辯論評分動態
- **實現**：CSS 動畫 + Moderator 每輪評分
- **技術**：無需新依賴，使用 Tailwind CSS keyframes

```css
@keyframes tugOfWar {
  from { width: 50%; }
  to { width: var(--score-width); }
}
```

##### 2. 語音合成（Text-to-Speech）
- **方案**：Web Speech API（零成本）
- **特色**：
  - Optimist：較高音調（pitch: 1.2）、略快語速（rate: 1.1）
  - Skeptic：較低音調（pitch: 0.8）、略慢語速（rate: 0.9）
- **升級路徑**：Phase 5+ 可改用 Google Cloud TTS / ElevenLabs

##### 3. Glitch Effect 按鈕
- **風格**：賽博龐克數位故障視覺
- **實現**：CSS 動畫 + text-shadow 偏移
- **顏色**：青色 + 洋紅色陰影、青綠色邊框發光

##### 4. 質詢環節（Cross-Examination）
- **機制**：快節奏問答，限制回應長度（max_tokens=100）
- **Prompt**：強制封閉式問題（Yes/No）
- **節奏**：利用 Groq 速度優勢製造緊張感

##### 5. 上帝模式（User Injection）
- **功能**：允許用戶中途注入突發事件
- **實現**：新增 SSE 事件 `user_injection`，將輸入作為 `HumanMessage` 注入 state

#### 🏗️ 建設性增強（Constructiveness Features）

##### 1. 謬誤偵測器（Fallacy Detective）
- **目標**：標記邏輯漏洞（人身攻擊、稻草人、訴諸情感等）
- **實現**：
  - Phase 3：基於規則的關鍵字檢測
  - Phase 4：使用 LLM 進行精確分析
- **UI**：類似足球黃牌，在對話泡泡旁彈出警告標籤

##### 2. 即時事實查核（Fact Check Cards）
- **目標**：側邊欄展示引用來源與驗證狀態
- **實現**：
  - 整合 Tavily 搜尋結果
  - 新增 SSE 事件 `fact_check`
  - 側邊欄顯示資料卡（來源、信心度、摘要）
- **Layout**：CSS Grid 三欄佈局（主對話 + 側邊欄）

##### 3. 結構化總結矩陣（Decision Matrix）
- **目標**：辯論結束後生成表格化比較
- **格式**：
  - 列（Rows）：爭點（經濟成本、道德風險、可行性）
  - 欄（Cols）：正方觀點 vs. 反方觀點
  - 格（Cells）：核心論據
- **實現**：Moderator 輸出 JSON，前端渲染為表格

##### 4. Reflection 機制（自我反思）
- **目標**：Agent 在發言後自我批評
- **流程**：
  1. Agent 發言
  2. Reflector 節點分析弱點
  3. 下一輪改進策略
- **Prompt**：「你的論點有什麼漏洞？對手可能如何反駁？」

#### 🤖 多模型配置策略

| 角色 | 模型 | 溫度 | 用途 | 成本/M tokens |
|------|------|------|------|---------------|
| **Optimist** | Qwen3 32B | 0.7 | 創意論述、中文優化 | $0.14 |
| **Skeptic** | Qwen3 32B | 0.6 | 理性批判、邏輯分析 | $0.14 |
| **Moderator** | GPT-OSS 120B | 0.3 | 評分總結、推理判斷 | $1.50 |
| **Router** | Llama 4 Scout | 0.0 | 工具決策、快速路由 | 最低 |
| **Fallback** | Llama 3.3 70B | 0.7 | 備用模型、容錯 | $0.27 |

**環境變數配置**：
```bash
OPTIMIST_MODEL=qwen/qwen3-32b
SKEPTIC_MODEL=qwen/qwen3-32b
MODERATOR_MODEL=openai/gpt-oss-120b
ROUTER_MODEL=llama-4-scout-17b
FALLBACK_MODEL=llama-3.3-70b-versatile
```

#### 📊 擴展階段時程

| 階段 | 時間 | 主要功能 | 狀態 |
|------|------|---------|------|
| **Phase 2.5** | 1 週 | 架構重構（Context API、SSE 擴展） | 🔄 計劃中 |
| **Phase 3** | 3-4 週 | 側邊欄、多模型、工具層、TTS | 🔄 計劃中 |
| **Phase 4** | 4-6 週 | Reflection、Moderator、質詢環節 | 📋 規劃中 |
| **Phase 5** | 2-3 週 | UI 美化、Glitch Effect、動畫 | 📋 規劃中 |

**總計**：Phase 2.5 → Phase 5 約 10-14 週完整實現

#### 🎯 關鍵技術決策

1. **保持 Token Streaming 架構**：不改用 LangGraph StateGraph，維持 main.py 直接 `llm.astream()` 優勢
2. **動畫零依賴**：使用 Tailwind CSS 原生 keyframes，不引入 framer-motion
3. **TTS 漸進式**：Phase 3 用 Web Speech API，Phase 5+ 升級到付費方案
4. **成本優化**：辯手用 Qwen3 32B（低成本），裁判用 GPT-OSS 120B（高質量）
5. **側邊欄響應式**：手機折疊為底部抽屜，平板/桌面顯示側邊欄

#### 📁 新增檔案結構預覽

```
frontend/app/
├── context/
│   └── DebateContext.tsx        # 全局狀態管理
├── hooks/
│   ├── useDebate.ts             # 辯論狀態 Hook
│   └── useTTS.ts                # TTS Hook
└── components/
    ├── FactCheckPanel.tsx       # 事實查核面板
    ├── FallacyBadges.tsx        # 謬誤標籤
    ├── ScoreBar.tsx             # 戰況拉鋸條
    └── MatrixSummary.tsx        # 結構化總結

backend/app/
├── models.py                    # 多模型配置管理
├── tools/
│   ├── web_search.py           # Tavily + DuckDuckGo
│   ├── fallacy_detector.py     # 謬誤檢測
│   └── fact_checker.py         # 事實查核
└── agents/
    ├── moderator.py            # 裁判 Agent
    └── reflector.py            # 反思邏輯
```

### 7.7 下一步行動

#### 立即行動（本週）
1. 📝 **更新計劃文件**：將進階功能規劃納入專案文檔
2. 🔧 **環境準備**：確認 Groq API 額度、申請 Tavily API Key
3. 🚀 **模型升級**：從 `llama-3.1-8b-instant` 升級到 `llama-3.3-70b-versatile`

#### Phase 2 完成後
1. 🏗️ **Phase 2.5**：重構前端狀態管理（Context API）
2. 🎨 **Phase 3**：實現側邊欄、多模型、TTS、戰況條
3. 🧠 **Phase 4**：Reflection、Moderator、質詢環節、上帝模式
4. ✨ **Phase 5**：UI 美化、Glitch Effect、動畫優化

#### 參考文件
- 📖 [進階功能完整規劃](/.claude/plans/compressed-brewing-frog.md)
- 📋 [實施指南](./IMPLEMENTATION.md)
- 📝 [架構決策文件](./docs/ARCHITECTURE_DECISIONS.md)

---

## 📄 授權

MIT License

---

## 📞 聯絡資訊

如有任何問題或建議，歡迎聯絡專案維護者。

---

**最後更新**：2025-12-10
**專案版本**：v0.2.0
**文件狀態**：✅ Phase 2 完成，進階功能規劃中
