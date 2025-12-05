# 📅 開發日記：DebateAI - Phase 1 基礎架構與部署

**日期**：2025-12-05  
**狀態**：✅ Phase 1 完成 (部署成功)  
**心情**：從 WSL 幽靈路徑的地獄爬出來，最後看到雲端上文字在跑的那一刻，爽！

---

## � 今日成就 (Highlights)

### 1. 解決 WSL 環境靈異事件

- 遭遇了 `Failed to translate path` 和 `WSL phantom state` 問題。
- **原因**：VS Code 殘留了舊的 WSL Session，且專案原本建在 Windows 檔案系統導致權限與路徑錯亂。
- **解法**：在 WSL 家目錄 (`~`) 重建專案，並強制重啟 VS Code 視窗，讓終端機回歸正軌。

### 2. 後端開發 (FastAPI + uv)

- 完成 `main.py` 基礎架構。
- **Regex CORS**：解決了 Cloudflare Pages 動態子網域 (`*.pages.dev`) 的跨域問題。
- **Fake SSE**：實作了模擬打字機效果的串流接口，並加上 `X-Accel-Buffering: no` 防止 Nginx/Cloudflare 搞事。
- **Docker 封裝**：寫好了 `Dockerfile`，使用 `uv` 進行極速依賴安裝。

### 3. 前端開發 (Next.js + shadcn/ui)

- **Cyberpunk UI**：引入 `shadcn/ui`，並魔改成 Emerald (樂觀) vs Rose (懷疑) 的對抗視覺風格。
- **串流優化**：捨棄 `EventSource`，改用 `fetch` + `ReadableStream` 支援 POST 請求。
- **State Management**：使用 `useRef` 建立 Buffer，解決了 React 在高速串流下 `useState` 不同步導致掉字的問題。
- **DebateUI 修正**：
  - 30 秒超時改為僅監控連線階段（首包後解除）
  - 連線時間在首包到達時記錄（而非整場結束後）
  - 停止時清空所有 buffer（避免殘留 UI 氣泡）

### 4. 雲端部署 (The Big Win)

#### Google Cloud Run (後端)

- 克服了 `uv` Buildpack 不支援的問題，改用 `gcloud builds submit` 先打包 Image 再部署。
- 設定了預算警告 ($5/mo) 與 `max-instances: 3` 防止破產。
- 成功解決 GCP 權限 (`Storage Admin`) 與 Billing 連結問題。

#### Cloudflare Pages (前端)

- 設定 `output: 'export'` 進行靜態導出。
- 使用 Wrangler CLI 一鍵上傳，成功與後端連線。
- 綁定自訂網域 `debateai.roy422.ggff.net`。

---

## 🐛 遇到的坑與解決方案 (Troubleshooting)

| 問題                      | 原因                                                 | 解決方案                                                           |
| :------------------------ | :--------------------------------------------------- | :----------------------------------------------------------------- |
| **WSL 找不到檔案**        | 專案建在 Windows 目錄且 WSL 重啟後路徑失效           | 在 WSL `~` 目錄重建專案，使用 `code .` 重新連線                    |
| **`uv sync` 失敗**        | hatchling 找不到套件目錄                             | 添加 `[tool.hatch.build.targets.wheel]` 到 pyproject.toml          |
| **Docker Build 失敗**     | `pyproject.toml` 參照了 README 但 Dockerfile 沒 COPY | 修改 Dockerfile 加入 `COPY README.md ./`                           |
| **GCP Permission Denied** | Cloud Build 機器人沒有讀取 Storage 的權限            | `gcloud projects add-iam-policy-binding` 賦予 `storage.admin`      |
| **Cloud Run 部署失敗**    | `uv` 環境不被 Google Buildpacks 支援                 | 放棄 `--source .`，改用 `gcloud builds submit` 強制使用 Dockerfile |
| **自訂網域 CORS 失敗**    | 只允許 `*.pages.dev`                                 | 添加 `*.ggff.net` 到 CORS regex                                    |

---

## 📊 部署資訊

| 服務 | 平台             | URL                                                 |
| ---- | ---------------- | --------------------------------------------------- |
| 前端 | Cloudflare Pages | https://debateai.roy422.ggff.net                    |
| 後端 | Cloud Run        | https://debate-api-1046434677262.asia-east1.run.app |

**GCP 配置**：

- Project ID: `debateai-480308`
- Region: `asia-east1`（台灣）
- 記憶體: 512Mi
- 最大實例數: 3

---

## 📸 里程碑

- ✅ 本地 `localhost:3000` 串流成功
- ✅ Cloud Run Health Check `{"status":"healthy"}`
- ✅ 正式網址運作正常，冷啟動提示顯示正確

---

# � 明日待辦 (Tomorrow's To-Do): Phase 2 注入靈魂

目前的辯論內容是寫死的 (Fake Data)，明天要讓它接上真的大腦。

## 1. LLM 整合 (The Brain)

- [ ] 申請 **Groq API Key** (速度快、免費額度夠)
- [ ] 在後端安裝 `langchain-groq` 與 `langgraph`
- [ ] 設定 `.env` 加入 `GROQ_API_KEY`

## 2. LangGraph 邏輯實作 (The Logic)

- [ ] 建立 `backend/app/graph.py`
- [ ] 定義 **State** (儲存對話歷史)
- [ ] 實作 **Optimist Node** (樂觀者 Prompt)
- [ ] 實作 **Skeptic Node** (懷疑者 Prompt)
- [ ] 設定 Graph 流程：Start -> Optimist -> Skeptic -> End

## 3. API 串接 (The Connection)

- [ ] 修改 `main.py`，將 `fake_debate_stream` 替換為 `graph.astream_events`
- [ ] 調整 SSE 輸出格式，確保與前端 `handleSSEEvent` 相容

## 4. 部署更新 (Update)

- [ ] 使用 `gcloud run services update` 更新後端環境變數 (加入 API Key)
- [ ] 重新 `gcloud builds submit` 並部署新版後端

---

## 💡 技術筆記

### shadcn/ui + Tailwind CSS 4

- Tailwind CSS 4 使用 `@import "tailwindcss"` 語法
- shadcn/ui 需要手動添加 CSS 變數到 `:root`
- 使用 `@layer base` 設定全域樣式

### Cloud Run + Cloudflare 跨域

- Cloud Run SSE 需要設定 `X-Accel-Buffering: no` 防止緩衝
- CORS 需要明確返回 `Access-Control-Allow-Origin`
- 自訂網域需要額外添加到 CORS 允許列表

### React 高頻串流狀態管理

- `useState` 在高頻更新時會有非同步問題
- 使用 `useRef` 建立 buffer 追蹤即時文字
- 定期同步 ref 到 state 觸發 UI 渲染

---

**備註**：Phase 3 (聯網搜尋) 和 Phase 4 (Playwright 深度爬蟲) 先暫緩，先把 AI 辯論的邏輯跑通最重要。明天見！
