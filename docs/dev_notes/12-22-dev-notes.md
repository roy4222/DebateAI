# 開發日記 2025-12-22

## 📋 今日目標
完成 Supabase + 自動化測試 的實作計畫

---

## ✅ 完成事項

### 1. 專案需求分析
分析課程要求完成度：
- ✅ React: Component, Props, Context
- ✅ Next.js Routing
- ❌ **Supabase** - 缺失，需補齊
- ✅ 部署 (Cloudflare Pages + Cloud Run)
- ✅ API (FastAPI)

### 2. 制定 Supabase + 測試 實作計畫

#### 核心功能
- **辯論歷史儲存** - 辯論結束後自動存入 Supabase
- **Sidebar 歷史顯示** - 仿 Google AI Studio，顯示最近 5 筆
- **歷史詳細頁** - `/history/[id]` 查看完整辯論內容

#### 關鍵設計決策

| 決策           | 選擇                   | 理由                                |
| :------------- | :--------------------- | :---------------------------------- |
| Auth           | 無驗證                 | 學校專案，簡化架構                  |
| RLS            | Public SELECT only     | Service Role Key 寫入，避免垃圾資料 |
| updated_at     | Service Layer 控制     | 減少 DB trigger 複雜度              |
| Message Schema | 版本化 (v1)            | 支援未來升級                        |
| Sidebar 刷新   | Callback + Local State | 儲存後立即顯示，無需全頁刷新        |
| CI 測試        | Mock Supabase          | 隔離外部依賴                        |

#### Message Schema v1
```typescript
interface StoredMessage {
  version: 1;
  type: "ai" | "human" | "system" | "tool";
  node: "optimist" | "skeptic" | "moderator" | null;
  content: string;
  roundInfo?: string;
  timestamp: string; // ISO 8601
}
```

### 3. 重要修正
- ❌ 移除 `public_insert` RLS policy
- ✅ Backend 使用 `SUPABASE_SERVICE_ROLE_KEY` 繞過 RLS 寫入

---

## 📁 計畫檔案變更

### Backend (4 files)
- `pyproject.toml` - 新增 supabase + test 依賴
- `app/supabase_client.py` - [NEW] Client singleton
- `app/services/debate_service.py` - [NEW] 核心邏輯 + 序列化
- `app/main.py` - 新增 4 個 REST endpoints

### Frontend (5 files)
- `app/lib/api.ts` - 新增 API 函數
- `app/components/DebateUI.tsx` - 自動儲存 + callback
- `components/app-sidebar.tsx` - 歷史區塊 + 本地更新
- `app/history/page.tsx` - [NEW] 列表頁
- `app/history/[id]/page.tsx` - [NEW] 詳細頁

### Testing (3 files)
- `backend/tests/` - pytest 測試
- `frontend/__tests__/` - vitest 測試
- `.github/workflows/test.yml` - CI workflow

---

## 🔜 下一步
開始實作 Part 1: Supabase CLI 設定 + Migration
