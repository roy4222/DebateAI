# 📅 開發日記：DebateAI - 12/20

**日期**：2025-12-20  
**狀態**：✅ Phase 3d 完成 + 雲端部署  
**版本**：0.3.4

---

## 🎉 今日成就 (Highlights)

### Phase 3c：ToolNode 架構重構 ✅ (早上)

| 檔案       | 變更內容                                                              |
| ---------- | --------------------------------------------------------------------- |
| `graph.py` | 引入 ToolNode、新增 `tool_callback_node`、重構 Agent 節點為僅決策模式 |
| `main.py`  | 添加診斷日誌、版本更新至 0.3.3                                        |

### Phase 3d：Moderator Agent 每輪總結 ✅ (下午)

| 檔案                | 變更內容                                                 |
| ------------------- | -------------------------------------------------------- |
| `graph.py`          | 新增 `moderator_node`、兩種總結 Prompt、修改輪數計數邏輯 |
| `main.py`           | 處理 moderator SSE 事件、版本更新至 0.3.4                |
| `MessageBubble.tsx` | 新增 moderator 藍色主題樣式 + react-markdown 渲染        |
| `badge.tsx`         | 新增 moderator variant                                   |
| `DebateUI.tsx`      | Message 介面支援 moderator 類型                          |

### 額外改進 ✅

- 安裝 `react-markdown` 渲染 Moderator 總結報告（支援標題、粗體、列表）
- 修復前端部署環境變數問題（`NEXT_PUBLIC_API_URL` 未正確設定）

---

## 🔧 今日解決的問題

| #   | 問題                           | 根因                                       | 解決方案                           |
| --- | ------------------------------ | ------------------------------------------ | ---------------------------------- |
| 1   | 搜尋指示器永遠不顯示           | 工具在節點內部手動調用，LangGraph 無法追蹤 | 使用 ToolNode 獨立執行工具         |
| 2   | round_count 顯示為 0           | 舊邏輯在 skeptic→optimist 時計數           | 改為在 skeptic→moderator 時計數    |
| 3   | Moderator 總結 Markdown 不渲染 | 前端只顯示純文字                           | 安裝 react-markdown + 自訂樣式組件 |
| 4   | 生產環境連接 localhost:8000    | Build 時未設定 NEXT_PUBLIC_API_URL         | Build 時指定環境變數再部署         |

---

## 📝 關鍵技術變更 (Phase 3d)

### 1. Moderator 節點

```python
async def moderator_node(state: DebateState) -> dict:
    current_round = state.get("round_count", 0) + 1
    is_final = (current_round >= state.get("max_rounds", 3))

    # 階段性總結 vs 最終報告
    if is_final:
        system_prompt = MODERATOR_FINAL_SUMMARY
    else:
        system_prompt = MODERATOR_ROUND_SUMMARY.format(round=current_round)

    return {
        "messages": [final_response],
        "current_speaker": "end" if is_final else "optimist",
        "round_count": current_round
    }
```

### 2. 流程變更

```
Phase 3c: Optimist → Skeptic → [3輪?] → END
Phase 3d: Optimist → Skeptic → Moderator → [3輪?] → Optimist/END
```

### 3. Markdown 渲染

```tsx
import ReactMarkdown from "react-markdown";

// Moderator 使用 Markdown 渲染
<ReactMarkdown
  components={{
    h2: ({ children }) => (
      <h2 className="text-lg font-bold text-blue-200">{children}</h2>
    ),
    strong: ({ children }) => (
      <strong className="font-bold text-blue-100">{children}</strong>
    ),
    // ...
  }}
>
  {text}
</ReactMarkdown>;
```

---

## 📊 專案進度

| 階段                       | 狀態    | 完成度 |
| -------------------------- | ------- | ------ |
| Phase 0（基礎架構）        | ✅ 完成 | 100%   |
| Phase 1（雲端部署）        | ✅ 完成 | 100%   |
| Phase 2（AI 辯論）         | ✅ 完成 | 100%   |
| Phase 3a（LangGraph 遷移） | ✅ 完成 | 100%   |
| Phase 3b（搜尋工具）       | ✅ 完成 | 100%   |
| Phase 3c（ToolNode 重構）  | ✅ 完成 | 100%   |
| Phase 3d（Moderator 總結） | ✅ 完成 | 100%   |

---

## 🚀 部署記錄

### 後端 (Cloud Run)

- **Revision**: `debate-api-00011-svl`
- **版本**: v0.3.4, Phase 3d
- **URL**: https://debate-api-1046434677262.asia-east1.run.app

### 前端 (Cloudflare Pages)

- **Revision**: `b69bff4a`
- **正式 URL**: https://debateai.roy422.ggff.net

---

## ✅ 驗證結果

- ✅ `/health` 返回 v0.3.4, Phase 3d
- ✅ 辯論流程：Optimist → Skeptic → Moderator → Complete
- ✅ 每輪結束後 Moderator 生成小結
- ✅ 最終輪 Moderator 生成完整報告
- ✅ Markdown 格式正確渲染（標題、粗體、列表）
- ✅ 前端藍色 Moderator 區塊正確顯示
- ✅ 生產環境部署成功

---

## 📌 下一步

1. 添加搜尋來源連結顯示
2. 改進搜尋進度顯示（如「找到 3 個網站」）
3. 考慮 Phase 4：用戶可調整辯論參數（輪數、語調等）
