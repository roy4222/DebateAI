
---

# 🏆 **多 Agent AI 協作與即時辯論平台**

**核心優勢：** 本專案能完美展示 **多 Agent 的複雜互動**、**LangGraph 流程控制** 和 **即時的聊天/辯論介面**，是履歷上證明高階 AI 工程能力的關鍵項目。

---

## 核心功能與技術亮點

### 1. 動態辯論室 (Dynamic Debate Chamber)

**目標：** 用戶設定主題，平台上的 Agents（扮演不同角色）進行即時、結構化的辯論。

| 角色 (Agent Node) | 職責與 LLM 特性 | LangGraph 流程展示點 |
| :--- | :--- | :--- |
| **Orchestrator** | 決定發言順序，並在 Agent 離題時將流程拉回。 | **流程控制：** 條件轉移 (誰發言) 與迴圈管理。 |
| **Optimist** | 始終從積極、樂觀的角度進行論證，調用 **Web Search** 找支持數據。 | **工具調用：** Agent 根據角色需求使用外部工具。 |
| **Skeptic** | 負責質疑 Optimist 論點，從風險、弱點角度反駁。 | **狀態管理：** Agent 需記住並引用前一個 Agent 的論點。 |
| **Moderator** | 在辯論結束後，總結雙方論點，並生成一個中立的結論報告。 | **流程結束：** 在達到特定輪數後終止迴圈，轉移到總結節點。 |

**▶ 網頁介面亮點：**

*   **即時串流：** 使用 **WebSocket/SSE** 串流顯示每個 Agent 的發言，模擬真人辯論。
*   **視覺化設計：** 為每個 Agent 設計專屬的頭像和身份標籤，強化互動體驗。

---

### 2. 專家角色扮演問答 (Expert Role-Play Consultation)

**目標：** 用戶選擇特定專業人士 Agent 來回答問題，並由另一個 Agent 進行事實校驗。

| 角色 (Agent Node) | 職責與 LLM 特性 | LangGraph 流程展示點 |
| :--- | :--- | :--- |
| **Persona Agent** | 扮演特定角色（ex: 科技創業家）。**可使用微調/開源模型**來加強角色性。 | **多模型切換：** 展示平台能快速為不同 Agent 切換模型 (ex: Groq + Llama 3)。 |
| **Fact Checker** | **核心！** 收到回答後，立即調用 Web Search 進行**事實檢驗 (Fact Check)**。 | **安全與準確性：** 具備企業級 **防幻覺 (Anti-Hallucination)** 功能，極具履歷價值。 |
| **Finalizer** | 整合 Persona 的回答和 Fact Checker 的註釋/更正，生成最終輸出。 | **結果整合與輸出。** |

**▶ 網頁介面亮點：**

*   **角色選擇器：** 用戶可快速選擇 Agent 扮演的身份。
*   **校驗標籤：** 在 Persona Agent 的回答中，用顏色或標籤標示出 **Fact Checker** 已確認或修正的部分。

---

## 🚀 技術棧的調整與強化 (履歷價值最大化)

| 領域            | 調整建議                                                                    | 履歷亮點 (Keyword)                             |
| :------------ | :---------------------------------------------------------------------- | :----------------------------------------- |
| **Agent 核心**  | 堅持 **LangGraph.js**，專注於 Agent 間的**溝通**、**迴圈**和**條件轉移**。                 | **Complex Multi-Agent Workflow**           |
| **即時性**       | **強化 WebSocket/SSE！** 讓 Agent 的「思考過程」和「工具調用」都即時在前端日誌中顯示。                | **Real-Time Log & Streaming Architecture** |
| **數據層 (RAG)** | **新增 VDB (向量資料庫)**：使用 **Cloudflare Vectorize/Chroma/LanceDB** 進行本地 RAG。 | **Hybrid Knowledge Retrieval (Web + RAG)** |
| **部署架構**      | **Cloudflare Workers/Pages + D1/KV** 實現全棧邊緣計算部署。                        | **Edge Computing & Full-Stack Deployment** |

---

# II. 專案最終架構與開發計畫 (Cloudflare Stack)

## 📌 專案架構目標

1.  **Agent 協作與流程控制（LangGraph.js）**
2.  **即時串流體驗（SSE/Streaming）**
3.  **雲端部署與架構設計（Cloudflare 全家桶）**

### 最終架構設計：全 Cloudflare

| 組件 | 技術選型 | 說明 |
| :--- | :--- | :--- |
| **前端 (UI)** | Next.js 16 + React 19 + Tailwind | 使用 App Router，部署在 **Cloudflare Pages**。 |
| **後端 (API)** | Cloudflare Workers + Hono + LangGraph.js | 一支 Worker 處理 API 路由與 LangGraph 流程。 |
| **資料層 (DB)** | Cloudflare KV 或 D1 (選配) | 儲存辯論歷史記錄 (`sessionId`, `messages`, `summary`)。 |
| **LLM 層** | Groq + OpenRouter (免費為優先) | 使用 **Groq (llama-3.1-8b)** 作為高性能模型，API Key 存於 Workers Secrets。 |

### MVP 功能規劃（第一版必須完成的）

1.  **多 Agent 辯論室（3–4 個 AI）**
    *   **流程：** `START` → `Orchestrator` → `Optimist` → `Orchestrator` → `Skeptic` → ... → `Moderator` → `END`。
    *   **使用者輸入：** 辯論主題、回合數。
2.  **即時串流與前端介面**
    *   **技術：** Workers 運行 LangGraph 時，透過 **SSE (Server-Sent Events)** 串流 Agent 輸出。
    *   **UI/UX：** 不同 Agent 使用不同的背景色/頭像（如 Optimist 綠、Skeptic 紅），顯示 `Agent 名稱 + 回合數 + 時間戳`。

---

## 🗺️ 開發階段計畫 (Roadmap)

### ⚪ Phase 0：平台打底 (Cloudflare Pages + Workers + SSE)
*   **目標：** 確認前後端部署與即時串流機制正常運作。
*   **實作：** Next.js 部署 Pages；Workers 建立 Hono 路由；實現 `GET /api/stream`，確認前端可接收 SSE 串流。

### 🔴 Phase 1：單場辯論 MVP (無資料庫)
*   **目標：** 實現一個不依賴 LangGraph 的手寫 Agent 辯論流程，確保 Cloudflare 環境下的 LLM 呼叫穩定性。
*   **實作：** 完成 `/debate` 頁面，建立 SSE 連線，顯示各 Agent 發言與總結。

### 🟡 Phase 2：導入 LangGraph.js (核心技術亮點)
*   **目標：** 將 Phase 1 的手寫流程抽象為 LangGraph 工作流。
*   **實作：** 定義 `DebateState`、Agent 節點 (`optimistNode`...) 和 `StateGraph`。Workers 內改為使用 `graph.stream()` 逐步取得輸出，並轉成 SSE 事件送給前端。

### 🟢 Phase 3：資料庫與歷史紀錄 (可選 V1.5)
*   **目標：** 增加資料持久化功能，提升專案完整度。
*   **實作：** 選擇 Cloudflare KV 或 D1 儲存辯論 JSON/資料表。前端新增 `/history` 頁面。

---

## 📈 總結：本專案的技術價值

選擇「AI 辯論與角色扮演平台」將讓您的專案具備：

*   **高度互動性：** 實時辯論讓用戶參與感極強。
*   **視覺化效果：** 即時聊天和角色頭像極度吸睛。
*   **技術深度：** 完美展示 **LangGraph 迴圈、多 Agent 溝通、事實校驗 (Fact Checking)** 等企業級 AI 應用所需的複雜技術。
*   **架構廣度：** 掌握 **Edge Computing (Cloudflare 全棧)** 和 **Real-Time Streaming (SSE)** 部署經驗。