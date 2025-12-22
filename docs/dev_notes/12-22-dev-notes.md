# 開發日記 2025-12-22

## 📋 今日目標
完成 Supabase 辯論歷史儲存 + 自動化測試整合

---

## ✅ 完成事項

### 1. Supabase 設定與資料庫建立
- ✅ 安裝 Supabase CLI (`brew install supabase/tap/supabase`)
- ✅ 初始化專案 (`supabase init`)
- ✅ 建立 Migration SQL
- ✅ 連結專案 (`supabase link --project-ref ixpckqbwjjchqjiaavbn`)
- ✅ 推送 Migration (`supabase db push`)

### 2. Backend 實作
- ✅ `pyproject.toml` - 新增 `supabase>=2.10.0` + 測試依賴
- ✅ `app/supabase_client.py` - Singleton client + `is_supabase_enabled()`
- ✅ `app/services/debate_service.py` - Message Schema v1 + CRUD
- ✅ `app/main.py` - 4 個新 API endpoints
  - `POST /debate/save` - 儲存辯論
  - `GET /debate/history` - 最近 5 筆
  - `GET /debate/history/list` - 分頁列表
  - `GET /debate/history/{id}` - 單筆詳細

### 3. Frontend 實作
- ✅ `app/lib/api.ts` - 新增 4 個 API 函數 + 類型定義
- ✅ `app/components/DebateUI.tsx` - 自動儲存 + Context 整合
- ✅ `components/app-sidebar.tsx` - 最近辯論區塊 (Google AI Studio 風格)
- ✅ `app/history/page.tsx` - 列表 + 詳細頁合併 (使用 query string)
- ✅ `contexts/DebateHistoryContext.tsx` - 共享狀態 Context
- ✅ `components/Providers.tsx` - Context Provider wrapper

### 4. 關鍵設計決策

| 決策           | 選擇               | 理由                                |
| :------------- | :----------------- | :---------------------------------- |
| Auth           | 無驗證             | 學校專案，簡化架構                  |
| RLS            | Public SELECT only | Service Role Key 寫入，避免垃圾資料 |
| Message Schema | 版本化 (v1)        | 支援未來升級                        |
| Sidebar 刷新   | Context + Ref      | 避免 stale closure                  |
| 動態路由       | Query string       | 相容 Next.js static export          |

---

## 🐛 遇到的問題與解決方案

### 問題 1: Supabase 環境變數未載入
**症狀:** `/health` 顯示 `supabase_enabled: false`
**原因:** `backend/.env` 缺少 `SUPABASE_URL` 和 `SUPABASE_SERVICE_ROLE_KEY`
**解決:** 手動加入環境變數並重啟後端

### 問題 2: handleSSEEvent stale closure
**症狀:** 自動儲存時 `topic` 為空或 sidebar 不更新
**原因:** `handleSSEEvent` 使用 `useCallback([])` 但呼叫的 `handleAutoSave` 依賴 state
**解決:** 新增 `currentTopicRef` 和 `addNewDebateRef`，使用 ref pattern 避免 closure 問題

### 問題 3: Next.js static export 不支援動態路由
**症狀:** Build 錯誤 `dynamicParams: true cannot be used with output: export`
**原因:** `/history/[id]` 動態路由無法預先生成
**解決:** 移除 `/history/[id]`，改用 `/history?id=xxx` query string + Suspense 包裝

### 問題 4: useSearchParams 需要 Suspense
**症狀:** Build 錯誤 `useSearchParams() should be wrapped in a suspense boundary`
**解決:** 將使用 `useSearchParams` 的元件用 `<Suspense>` 包裝

### 問題 5: 前端 API 請求 404
**症狀:** 儲存辯論時收到 HTTP 404
**原因:** `frontend/.env` 指向 Cloud Run 生產環境，但新 API 尚未部署
**解決:** 本地測試時改用 `NEXT_PUBLIC_API_URL="http://localhost:8000"`

---

## 📁 檔案變更總覽

### Backend (新增/修改)
```
backend/
├── pyproject.toml              # [MODIFIED] 新增依賴
├── app/
│   ├── supabase_client.py      # [NEW] Supabase client singleton
│   ├── main.py                 # [MODIFIED] 4 個新 endpoints
│   └── services/
│       ├── __init__.py         # [NEW]
│       └── debate_service.py   # [NEW] 核心業務邏輯
```

### Frontend (新增/修改)
```
frontend/
├── app/
│   ├── lib/api.ts              # [MODIFIED] 新增 API 函數
│   ├── components/DebateUI.tsx # [MODIFIED] 自動儲存
│   ├── layout.tsx              # [MODIFIED] 新增 Provider
│   └── history/
│       └── page.tsx            # [NEW] 歷史頁面
├── components/
│   ├── app-sidebar.tsx         # [MODIFIED] 歷史區塊
│   └── Providers.tsx           # [NEW] Context wrapper
└── contexts/
    └── DebateHistoryContext.tsx # [NEW] 共享狀態
```

### Supabase
```
supabase/
├── config.toml
└── migrations/
    └── 20251222065406_create_debate_history.sql  # [NEW]
```

---

## 🔜 待辦事項

### Testing + CI/CD
- [ ] Backend 測試 (pytest)
  - [ ] `tests/conftest.py` - Mock Supabase
  - [ ] `tests/test_service.py` - debate_service 單元測試
  - [ ] `tests/test_main.py` - API 整合測試
- [ ] Frontend 測試 (Vitest)
  - [ ] `__tests__/lib/api.test.ts`
  - [ ] `__tests__/components/*.test.tsx`
- [ ] GitHub Actions
  - [ ] `.github/workflows/test.yml`

### 部署
- [ ] 更新 Cloud Run 後端 (含新 API)
- [ ] 更新 Cloudflare Pages 前端
- [ ] 設定生產環境 Supabase 環境變數
