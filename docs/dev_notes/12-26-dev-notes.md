# 開發日記 2025-12-26

## 📋 今日目標

1. i18n 國際化實作（中英雙語）
2. Groq API 限流容錯機制優化
3. 修復 CI/CD 測試失敗問題

---

## ✅ 完成事項

### 1. 國際化（i18n）完整實作 ✅

#### Backend 中英雙語支援

**檔案：`backend/app/graph.py`**
- ✅ 移除全域 `current_language` 變數（避免 race condition）
- ✅ 將 `language: str` 加入 `DebateState` TypedDict
- ✅ 新增中英雙語系統提示詞：
  - `OPTIMIST_SYSTEM_EN` / `OPTIMIST_SYSTEM_ZH`
  - `SKEPTIC_SYSTEM_EN` / `SKEPTIC_SYSTEM_ZH`
  - `MODERATOR_SYSTEM_EN` / `MODERATOR_SYSTEM_ZH`
- ✅ 更新所有函數接受 `language` 參數：
  - `get_optimist_system(language)`
  - `get_skeptic_system(language)`
  - `get_moderator_system(language)`
  - `build_prompt(state, speaker, language)`
  - `create_initial_state(topic, max_rounds, language)`
- ✅ 所有節點（optimist_node, skeptic_node, moderator_node）使用 `state['language']`

**檔案：`backend/app/main.py`**
- ✅ `DebateRequest` 新增 `language` 欄位（pattern validation: `^(zh|en)$`）
- ✅ SSE 訊息完整 i18n（29 處中英對照）：
  - 連線訊息："Connecting to AI Debate Engine..." / "正在喚醒 AI 辯論引擎..."
  - 模型資訊："Using model: xxx" / "使用模型: xxx"
  - 回合標記："Round 1" / "第 1 輪"
  - 角色名稱："Optimist" / "樂觀者"
  - 工具搜尋："Searching: xxx" / "搜尋: xxx"
  - 完成訊息："Debate complete!" / "辯論結束！"

#### Frontend 中英雙語支援

**檔案：`frontend/lib/i18n.tsx`**
- ✅ 完整翻譯字典（50+ 條目）
- ✅ 修正 localStorage key 為 `'debateai-locale'`（與 layout.tsx 統一）
- ✅ 移除 cookie 管理（不支援 static export）
- ✅ 同步 `document.documentElement.lang` 屬性

**檔案：`frontend/app/layout.tsx`**
- ✅ 新增 inline script 立即同步 lang 屬性（避免閃爍）
- ✅ 文件化 static export 限制

**檔案：`frontend/app/lib/api.ts`**
- ✅ 錯誤訊息 i18n：
  - "Debate stopped" / "辯論已停止"
  - "Unknown error" / "未知錯誤"

**檔案：`frontend/README.md`**
- ✅ 移除誤植的 "py" 行

---

### 2. LLM Fallback 機制重構 ✅

#### 問題診斷

**原問題**：遇到 429 rate limit 時，系統會重試**同一個模型**，而非切換 fallback。

**根本原因**：
- 自定義 `RateLimitRetryLLM` 包裝器無法在 retry 內切換模型
- Groq SDK 的 `max_retries > 0` 會在內部重試同一模型 5 秒，阻止 LangChain fallback 觸發

**Log 證據**：
```
22:20:11 - POST openai/gpt-oss-120b → 429 Too Many Requests
22:20:11 - Retrying request in 5.000000 seconds  ❌
22:20:16 - POST openai/gpt-oss-120b → 200 OK     ❌ 沒切換 fallback
```

#### 解決方案

**採用 LangChain 原生 `with_fallbacks()` 機制**

**檔案：`backend/app/graph.py`**

**關鍵修改**：
1. ✅ **移除** `RateLimitRetryLLM` 類別（~100 行）
2. ✅ **重寫** `get_llm()` 函數：
   ```python
   def get_llm(bind_tools: bool = False):
       # 主要模型
       primary_llm = ChatGroq(
           model="openai/gpt-oss-120b",
           max_retries=0,  # ✅ 關鍵：不在 SDK 層重試
           timeout=30.0,
           api_key=api_key
       )

       # ✅ 關鍵：先綁定工具，再做 fallback
       if bind_tools:
           primary_llm = primary_llm.bind_tools(tools)

       # 建立 fallback 鏈
       fallback_llms = [...]
       for fallback_llm in fallback_llms:
           if bind_tools:
               fallback_llm = fallback_llm.bind_tools(tools)

       # LangChain fallback 機制
       return primary_llm.with_fallbacks(
           fallbacks=fallback_llms,
           exceptions_to_handle=(
               RateLimitError,
               APIError,
               HTTPStatusError,  # ✅ 捕獲 429
               RequestError,
               TimeoutException
           )
       )
   ```

3. ✅ **修正** API 參數名：`groq_api_key` → `api_key`
4. ✅ **修正** import：`httpx.Timeout` → `httpx.TimeoutException`
5. ✅ **新增** `HTTPStatusError` 和 `RequestError` 到異常處理

**Fallback 順序**：
1. `openai/gpt-oss-120b` (Groq, 免費最快)
2. `moonshotai/kimi-k2-instruct-0905` (Moonshot, 備援)
3. `llama-3.1-8b-instant` (Groq 官方模型, 最終備援)

**預期行為**：
```
[DEBUG] Attempting: openai/gpt-oss-120b
[ERROR] HTTPStatusError: 429 Too Many Requests (立即拋出)
[INFO] Fallback triggered → moonshotai/kimi-k2-instruct-0905
[DEBUG] Fallback model response successful ✅
```

---

### 3. 測試重構與 CI 修復 ✅

#### Backend 測試更新

**檔案：`backend/tests/test_graph.py`**

**移除**：`TestRateLimitRetryLLM` 類別（4 個測試）
- 測試已廢棄的 `RateLimitRetryLLM` 類別

**新增**：`TestLLMFallback` 類別（3 個測試）
- `test_get_llm_returns_runnable` - 驗證返回 LangChain Runnable
- `test_fallback_configured_with_exceptions` - 驗證 fallback 配置
- `test_max_retries_is_zero` - 煙霧測試

**更新**：`TestGetLLM` 類別（3 個測試）
- 移除對 `RateLimitRetryLLM` 的引用
- 改為驗證返回的是 `Runnable` 實例

**測試結果**：
- ✅ 59 passed, 0 failed
- ✅ Coverage: **76.75%** ⬆️（原 57%）

#### Frontend 測試修復

**問題**：`MessageBubble` 和 `TopicForm` 使用 `useI18n` hook，但測試缺少 `I18nProvider`

**解決方案**：

**新增檔案：`frontend/app/__tests__/test-utils.tsx`**
```typescript
export function renderWithProviders(ui: React.ReactElement) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return <I18nProvider>{children}</I18nProvider>
  }
  return render(ui, { wrapper: Wrapper })
}

export { renderWithProviders as render }
export * from '@testing-library/react'
```

**更新測試檔案**：
- `frontend/app/components/__tests__/MessageBubble.test.tsx`
- `frontend/app/components/__tests__/TopicForm.test.tsx`

```typescript
// 修改前
import { render, screen } from "@testing-library/react";

// 修改後
import { render, screen } from "@/app/__tests__/test-utils";
```

**測試結果**：
- ✅ 37 passed, 0 failed
- ✅ 所有測試檔案通過

---

## 📊 最終測試成績

### Backend Tests（pytest）

| 測試檔案                  | 測試數 | 狀態 | 測試內容                            |
| ------------------------- | ------ | ---- | ----------------------------------- |
| `test_graph.py`           | 13     | ✅   | LangGraph 狀態、LLM Fallback 機制   |
| `test_main.py`            | 15     | ✅   | FastAPI API 端點、CORS 設定         |
| `test_service.py`         | 17     | ✅   | Supabase CRUD、訊息序列化           |
| `test_search.py`          | 7      | ✅   | 搜尋工具容錯、優雅降級              |
| `test_supabase_client.py` | 7      | ✅   | 客戶端初始化、狀態檢查              |
| **總計**                  | **59** | ✅   | **76.75% 覆蓋率**（門檻 50%）       |

### Frontend Tests（Vitest）

| 測試檔案                 | 測試數 | 狀態 | 測試內容                 |
| ------------------------ | ------ | ---- | ------------------------ |
| `api.test.ts`            | 13     | ✅   | API 客戶端、SSE 串流處理 |
| `TopicForm.test.tsx`     | 13     | ✅   | 表單互動、按鈕狀態       |
| `MessageBubble.test.tsx` | 11     | ✅   | 訊息渲染、角色配置       |
| **總計**                 | **37** | ✅   | **所有測試通過**         |

### 覆蓋率詳情（Backend）

| 檔案                 | 覆蓋率  | 變化   | 說明             |
| -------------------- | ------- | ------ | ---------------- |
| `supabase_client.py` | 100%    | -      | ✅ 完全覆蓋      |
| `graph.py`           | **86%** | ⬆️ +41% | ✅ 大幅提升      |
| `search.py`          | 84%     | ⬆️ +5%  | ✅ 高覆蓋        |
| `debate_service.py`  | 84%     | -      | ✅ 高覆蓋        |
| `main.py`            | 60%     | ⬆️ +8%  | SSE 串流部分未測 |
| **總計**             | **77%** | ⬆️ +20% | 超過 50% 門檻 ✅ |

---

## 📁 檔案變更總覽

### Backend 主要變更

```
backend/
├── app/
│   ├── graph.py              # [MODIFIED]
│   │   - 移除 RateLimitRetryLLM 類別
│   │   - 實作 with_fallbacks() 機制
│   │   - 新增 language 參數支援
│   │   - 中英雙語系統提示詞
│   │   - max_retries=0 關鍵修復
│   │
│   └── main.py               # [MODIFIED]
│       - DebateRequest 新增 language 驗證
│       - SSE 訊息完整 i18n
│       - real_debate_stream() 中英雙語
│       - langgraph_debate_stream() 中英雙語
│
└── tests/
    └── test_graph.py         # [MODIFIED]
        - 移除 TestRateLimitRetryLLM
        - 新增 TestLLMFallback
        - 更新 TestGetLLM
```

### Frontend 主要變更

```
frontend/
├── app/
│   ├── __tests__/
│   │   └── test-utils.tsx       # [NEW] I18nProvider wrapper
│   │
│   ├── lib/
│   │   ├── i18n.tsx             # [MODIFIED] localStorage key 修正
│   │   ├── api.ts               # [MODIFIED] 錯誤訊息 i18n
│   │   └── __tests__/
│   │       └── api.test.ts      # [NO CHANGE] language 有預設值
│   │
│   ├── components/__tests__/
│   │   ├── MessageBubble.test.tsx  # [MODIFIED] 使用 test-utils
│   │   └── TopicForm.test.tsx      # [MODIFIED] 使用 test-utils
│   │
│   └── layout.tsx               # [MODIFIED] inline script + localStorage key
│
└── README.md                    # [MODIFIED] 移除誤植
```

---

## 🐛 問題修復記錄

### 高優先級

1. **全域語言狀態 race condition** ✅
   - 問題：多個請求共用 `current_language` 導致語言混亂
   - 解決：移至 `DebateState`，每個辯論獨立語言設定

2. **Fallback 模型未切換** ✅
   - 問題：429 錯誤時重試同模型，未觸發 fallback
   - 解決：`max_retries=0` + LangChain `with_fallbacks()`

3. **測試失敗（CI）** ✅
   - Backend：`RateLimitRetryLLM` import error
   - Frontend：缺少 `I18nProvider` context
   - 解決：重構測試 + 新增 test-utils

### 中優先級

4. **localStorage key 不一致** ✅
   - 問題：`'debate-language'` vs `'debateai-locale'`
   - 解決：統一為 `'debateai-locale'`

5. **SSE 訊息仍為中文** ✅
   - 問題：`main.py` 硬編碼中文訊息
   - 解決：29 處中英對照實作

6. **Tool binding 與 fallback 衝突** ✅
   - 問題：`with_fallbacks()` 後 `bind_tools()` 導致 fallback 模型無工具
   - 解決：先 `bind_tools()` 再 `with_fallbacks()`

### 低優先級

7. **HTML lang 屬性靜態** ✅
   - 問題：Next.js static export 無法 SSR 動態設定
   - 解決：inline script 客戶端同步 + 文件化限制

8. **README typo** ✅
   - 問題：多餘的 "py" 行
   - 解決：刪除

---

## 💡 技術亮點

### 1. LangChain Fallback 最佳實踐

**關鍵發現**：Groq SDK 的 `max_retries` 會攔截錯誤，必須設為 `0` 才能讓 LangChain fallback 生效。

**正確順序**：
```python
llm = ChatGroq(max_retries=0, ...)
if bind_tools:
    llm = llm.bind_tools(tools)  # 先綁定工具
llm_with_fallbacks = llm.with_fallbacks(...)  # 再做 fallback
```

### 2. Static Export 的 i18n 權衡

**限制**：無法在 SSR 時動態設定 `<html lang>`

**解決方案**：
- SSR HTML 永遠是 `lang="zh-TW"`（預設中文）
- 客戶端 inline script 立即同步（避免閃爍）
- SEO/無 JS 環境仍看到合理的預設語言

### 3. 測試工具模式

**Pattern**：創建 `test-utils.tsx` 統一管理測試 Provider

**優點**：
- 避免每個測試重複包裝
- 未來可輕鬆新增其他 Provider（ThemeProvider 等）
- 符合 React Testing Library 最佳實踐

---

## 🔜 待辦事項

### 高優先級

- [x] ~~i18n 完整實作~~
- [x] ~~Fallback 機制修復~~
- [x] ~~CI 測試通過~~

### 中優先級

- [ ] 設定 GitHub Secrets 啟用自動部署
- [ ] 提高覆蓋率到 80%（目前 77%）
- [ ] 新增 E2E 測試（Playwright）

### 低優先級

- [ ] Supabase 安全性（anon key + RLS）
- [ ] 監控 Groq API 使用量統計
- [ ] 新增更多 fallback 模型

---

## 📈 今日成就

- ✅ **i18n**: 中英雙語完整支援（Backend + Frontend）
- ✅ **Fallback**: LangChain 原生機制，穩定可靠
- ✅ **測試**: 96 個測試全部通過（59 Backend + 37 Frontend）
- ✅ **覆蓋率**: Backend 從 57% → 77% ⬆️ **+20%**
- ✅ **CI/CD**: 所有 workflow 通過 ✅

**總修改**：
- 11 個檔案修改
- 1 個新檔案（test-utils.tsx）
- ~200 行程式碼變更
- 100% 測試通過率
