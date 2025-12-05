# 📅 開發日記：DebateAI - Phase 1 & 2

**日期**：2025-12-05  
**狀態**：✅ Phase 2 完成 (真實 AI 辯論上線)  
**心情**：從 fake 模板到真正的 AI 辯論，看到 Groq 串流飆出來那一刻，爽上加爽！

---

## 🎉 今日成就 (Highlights)

### Phase 1 回顧（早上完成）

- 解決 WSL 環境靈異事件
- 後端開發 (FastAPI + uv + Regex CORS + Fake SSE)
- 前端開發 (Next.js + shadcn/ui + 串流優化)
- 雲端部署 (Cloud Run + Cloudflare Pages)

### Phase 2 新增（晚上完成）

#### 1. 後端 LLM 整合

- **graph.py**：狀態管理模組
  - `DebateState` TypedDict 定義
  - `build_prompt()` 生成 Agent 專屬 Prompt
  - `update_state_after_speaker()` 狀態更新邏輯
- **main.py**：真正的 Token-Level 串流
  - 直接呼叫 `llm.astream()` 實現逐字輸出
  - `sse_event()` 輔助函數確保正確的 `\n\n` 格式
  - 錯誤處理與 fallback 機制

#### 2. 依賴更新

```toml
# pyproject.toml 新增
langchain>=0.3.0
langchain-groq>=0.2.0
langgraph>=1.0.0
```

#### 3. 環境變數

| 變數              | 用途                            |
| ----------------- | ------------------------------- |
| `GROQ_API_KEY`    | Groq API 金鑰                   |
| `GROQ_MODEL`      | 模型選擇 (llama-3.1-8b-instant) |
| `USE_FAKE_STREAM` | 強制使用假資料 (測試用)         |

---

## 🐛 遇到的坑與解決方案 (Troubleshooting)

| 問題                          | 原因                                                        | 解決方案                                                     |
| ----------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------ |
| **前端收不到 SSE 事件**       | 後端使用 `\\n\\n` 輸出字面字串而非換行符                    | 建立 `sse_event()` 輔助函數確保正確的 `\n\n`                 |
| **LangGraph 無法 token 串流** | `astream(stream_mode="messages")` 只在訊息加入 state 時串流 | 放棄 LangGraph 控制流，改為 main.py 直接呼叫 `llm.astream()` |
| **回合數顯示 0**              | `round_count` 在發送 speaker 事件後才遞增                   | 計算時使用 `round_count + 1`                                 |

---

## 📊 生產環境狀態

```bash
curl https://debate-api-1046434677262.asia-east1.run.app/health
```

```json
{
  "status": "healthy",
  "version": "0.2.0",
  "phase": 2,
  "has_groq_key": true,
  "use_fake_stream": false,
  "model": "llama-3.1-8b-instant"
}
```

---

## 📸 里程碑

- ✅ Phase 1 完成：Fake SSE 串流 + 雲端部署
- ✅ Phase 2 完成：真實 AI 辯論
  - Groq API 整合
  - Token-level 串流（打字機效果）
  - Optimist vs Skeptic 雙 Agent 交替

---

## 🔮 明日待辦：Bug 修復 & Phase 3

### 🐛 待修復 Bug

- [ ] **輸入的問題沒有保留在網頁上**：辯論開始後，用戶輸入的主題沒有顯示在頁面上方
- [ ] **輸入框沒有清空**：點擊「開始辯論」後，輸入框應該被清空

### Phase 3 聯網搜尋

### 1. 工具整合

- [ ] 安裝 `tavily-python` 或 `duckduckgo-search`
- [ ] 建立 `search_tool` 函數
- [ ] 在 Agent Prompt 中加入工具使用指引

### 2. LangGraph 重新引入

- [ ] 使用 LangGraph 管理工具調用流程
- [ ] 實作 `tool_node` 處理搜尋結果
- [ ] 串流搜尋進度到前端

### 3. 前端優化

- [ ] 顯示搜尋中狀態
- [ ] 展示引用來源連結

---

## 💡 技術筆記

### SSE 格式注意事項

```python
# ❌ 錯誤：\\n\\n 會輸出字面反斜線
yield f"data: {json.dumps(data)}\\n\\n"

# ✅ 正確：使用輔助函數
def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"
```

### Groq 串流 API

```python
from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant", streaming=True)

async for chunk in llm.astream(messages):
    if chunk.content:
        yield sse_event({'type': 'token', 'text': chunk.content})
```

### LangGraph 限制

`astream(stream_mode="messages")` 只會在訊息 **加入 state** 時觸發串流。如果節點內部使用 `llm.astream()`，tokens 不會被攔截。

**解法**：在節點外部直接控制 LLM 串流，LangGraph 只用於狀態管理。

---

**備註**：Phase 2 比想像中複雜，SSE 格式和 LangGraph 串流都踩了坑。但最後成功了！明天繼續 Phase 3！
