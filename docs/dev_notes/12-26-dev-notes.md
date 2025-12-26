# 開發日記 2025-12-26

## 📋 今日目標

Groq API 限流容錯機制 + Testing + CI/CD 完整實作

---

## ✅ 完成事項

### 1. Groq API Rate Limit 模型切換機制

- ✅ `app/graph.py` - 新增 `RateLimitRetryLLM` 包裝器類別
  - 遇到 429 限流錯誤時自動切換到備用模型
  - 維護「已限流」模型集合，避免重複嘗試
  - 所有模型都限流時，等待 10 秒後重置

### 2. Testing Infrastructure ✅

#### Backend pytest（60 個測試全部通過）

| 測試檔案                  | 測試數 | 測試內容                            |
| ------------------------- | ------ | ----------------------------------- |
| `test_graph.py`           | 14     | LangGraph 狀態、Rate Limit 重試機制 |
| `test_main.py`            | 15     | FastAPI API 端點、CORS 設定         |
| `test_service.py`         | 17     | Supabase CRUD、訊息序列化           |
| `test_search.py`          | 7      | 搜尋工具容錯、優雅降級              |
| `test_supabase_client.py` | 7      | 客戶端初始化、狀態檢查              |

#### Frontend Vitest（37 個測試全部通過）

| 測試檔案                 | 測試數 | 測試內容                 |
| ------------------------ | ------ | ------------------------ |
| `api.test.ts`            | 13     | API 客戶端、SSE 串流處理 |
| `TopicForm.test.tsx`     | 13     | 表單互動、按鈕狀態       |
| `MessageBubble.test.tsx` | 11     | 訊息渲染、角色配置       |

### 3. GitHub Actions CI/CD ✅ 驗證成功

- ✅ `.github/workflows/backend-test.yml` - Backend 測試
- ✅ `.github/workflows/frontend-test.yml` - Frontend 測試
- ✅ `.github/workflows/ci-cd.yml` - 整合 pipeline

**CI 執行結果**：

- Backend: 60 passed, 覆蓋率 57%（門檻 50%）
- Frontend: 37 passed
- 執行時間: ~24 秒

### 4. Code Review 修復

- ✅ `max_rounds` 驗證（限制 1-5 輪）
- ✅ `topic` 長度限制（最多 200 字）
- ✅ `AppSidebar` SSR window 檢查

### 5. 覆蓋率報告（CI 環境）

| 檔案                 | 覆蓋率  | 說明             |
| -------------------- | ------- | ---------------- |
| `supabase_client.py` | 100%    | ✅ 完全覆蓋      |
| `debate_service.py`  | 84%     | ✅ 高覆蓋        |
| `search.py`          | 79%     | ✅ 高覆蓋        |
| `main.py`            | 52%     | SSE 串流未測試   |
| `graph.py`           | 45%     | LangGraph 節點   |
| **總計**             | **57%** | 超過 50% 門檻 ✅ |

---

## 📁 檔案變更總覽

### Backend

```
backend/
├── app/
│   ├── graph.py              # [MODIFIED] RateLimitRetryLLM
│   └── main.py               # [MODIFIED] DebateRequest 驗證
├── tests/
│   ├── __init__.py           # [NEW]
│   ├── conftest.py           # [NEW] pytest fixtures
│   ├── test_graph.py         # [NEW] 14 tests
│   ├── test_main.py          # [NEW] 15 tests
│   ├── test_service.py       # [NEW] 17 tests
│   ├── test_search.py        # [NEW] 7 tests
│   └── test_supabase_client.py # [NEW] 7 tests
├── pytest.ini                # [NEW] pytest 設定
└── .coveragerc               # [NEW] 覆蓋率設定
```

### Frontend

```
frontend/
├── app/
│   ├── lib/__tests__/
│   │   └── api.test.ts          # [NEW] 13 tests
│   └── components/__tests__/
│       ├── TopicForm.test.tsx   # [NEW] 13 tests
│       └── MessageBubble.test.tsx # [NEW] 11 tests
├── components/
│   └── app-sidebar.tsx       # [MODIFIED] SSR 修復
├── vitest.config.ts          # [NEW]
└── vitest.setup.ts           # [NEW]
```

### GitHub Actions

```
.github/workflows/
├── backend-test.yml          # [NEW]
├── frontend-test.yml         # [NEW]
└── ci-cd.yml                 # [NEW]
```

---

## 🔜 待辦事項

### 中優先級

- [ ] 設定 GitHub Secrets 啟用自動部署
- [ ] 提高覆蓋率到 70%

### 低優先級

- [ ] Supabase 安全性（anon key + RLS）
- [ ] 監控 Groq API 使用量統計
