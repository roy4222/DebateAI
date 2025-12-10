# 📅 開發日記：DebateAI - 12/10

**日期**：2025-12-10  
**狀態**：✅ UI Bug 修復 + 進階功能規劃完成  
**心情**：今天解決了環境變數的坑，還完成了 Phase 4+ 的完整規劃！

---

## 🎉 今日成就 (Highlights)

### 1. UI Bug 修復

| Bug                  | 解決方案                                                | 檔案           |
| -------------------- | ------------------------------------------------------- | -------------- |
| 辯論主題沒有保留顯示 | 新增 `currentTopic` state，開始時保存主題並顯示為 Badge | `DebateUI.tsx` |
| 輸入框沒有清空       | 在 `startDebate()` 中呼叫 `setTopic("")`                | `DebateUI.tsx` |

### 2. 部署問題排查

- **問題**：生產環境嘗試連接 `localhost:8000`
- **根因**：`.env.local` 優先級高於 `.env.production`
- **解法**：build 前暫時移除 `.env.local`

### 3. 文檔更新

- 新增 `docs/網頁部署指南.md`：完整的前後端部署步驟
- 更新 `README.md`：加入 Phase 4+ 進階功能規劃

---

## 🐛 遇到的坑 (Troubleshooting)

| 問題                      | 原因                                               | 解決方案                                         |
| ------------------------- | -------------------------------------------------- | ------------------------------------------------ |
| **env 沒有自動帶入**      | gcloud deploy 中 `${GROQ_API_KEY}` 沒有 export     | 加入 `export $(grep -v '^#' .env \| xargs)` 步驟 |
| **生產環境連 localhost**  | Next.js 的 `.env.local` 優先級 > `.env.production` | Build 前先 `mv .env.local .env.local.bak`        |
| **ERR_BLOCKED_BY_CLIENT** | 瀏覽器擴充套件擋住請求（可能是 AdBlock）           | 確認不是 CORS 問題，是前端 API URL 錯誤          |

---

## 📝 進階功能規劃 (Phase 4+)

### 觀賞性增強

- [ ] 戰況拉鋸條（Tug-of-War Bar）
- [ ] 語音合成（Web Speech API）
- [ ] 質詢環節（Cross-Examination）
- [ ] 上帝模式（User Injection）

### 建設性增強

- [ ] 謬誤偵測器（Fallacy Detective）
- [ ] 即時事實查核（Fact Check Cards）
- [ ] 結構化總結矩陣（Decision Matrix）
- [ ] Reflection 機制（自我反思）

### 多模型配置策略

| 角色 | 模型          | 用途               |
| ---- | ------------- | ------------------ |
| 辯手 | Qwen3 32B     | 中文優化、創意論述 |
| 裁判 | GPT-OSS 120B  | 邏輯推理、評分總結 |
| 路由 | Llama 4 Scout | 工具決策、快速路由 |

---

## 💡 技術筆記

### Next.js 環境變數優先級

```
.env.local > .env.production > .env
```

> ⚠️ **重要**：`.env.local` 會覆蓋所有其他 `.env.*` 檔案！
>
> 部署前務必檢查或移除 `.env.local`

### 正確的部署流程

```bash
cd frontend
mv .env.local .env.local.bak   # 暫時移除
npm run build                   # 使用 .env.production
npx wrangler pages deploy out --project-name debate-ai
mv .env.local.bak .env.local   # 還原
```

---

## 📊 專案進度

| 階段                | 狀態      | 完成度 |
| ------------------- | --------- | ------ |
| Phase 0（基礎架構） | ✅ 完成   | 100%   |
| Phase 1（雲端部署） | ✅ 完成   | 100%   |
| Phase 2（AI 辯論）  | ✅ 完成   | 100%   |
| Phase 3（工具整合） | 🔄 待開始 | 0%     |

**整體完成度**：75%

---

## 🔮 明日待辦

### 高優先級

- [ ] 開始 Phase 3：安裝 `tavily-python`
- [ ] 實作三層容錯搜尋（Tavily → DuckDuckGo → 優雅降級）
- [ ] 前端顯示搜尋狀態指示器

### 中優先級

- [ ] 重構後端支援多模型配置
- [ ] 實作 Moderator Agent（總結報告）

### 低優先級

- [ ] 戰況拉鋸條 UI 設計
- [ ] Glitch Effect 按鈕樣式

---

**備註**：今天把 Phase 4+ 的完整規劃都寫進 README 了，非常滿意！明天開始真正進入 Phase 3，讓 Agent 會上網搜尋！🚀
