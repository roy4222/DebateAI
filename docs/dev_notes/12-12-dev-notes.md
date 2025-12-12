# 📅 開發日記：DebateAI - 12/12

**日期**：2025-12-12  
**狀態**：✅ Phase 3a 完成 - LangGraph StateGraph 遷移  
**心情**：Token 串流驗證成功！LangGraph 的 stream_mode="messages" 真的有效！

---

## 🎉 今日成就 (Highlights)

### Phase 3a：LangGraph StateGraph 遷移

| 檔案       | 變更內容                                                                 |
| ---------- | ------------------------------------------------------------------------ |
| `graph.py` | 新增 `optimist_node`、`skeptic_node`、`should_continue`、`debate_graph`  |
| `main.py`  | 新增 `langgraph_debate_stream()`、`USE_LANGGRAPH` 開關、版本升級到 0.3.0 |

### 關鍵技術決策

- **State 合併**：`messages` 使用 `Annotated[..., add_messages]` 自動合併
- **串流模式**：`debate_graph.astream(state, stream_mode="messages")`
- **回退機制**：`USE_LANGGRAPH=false` 可切回 `real_debate_stream()`

---

## 📝 技術筆記

### LangGraph StateGraph 架構

```
create_initial_state(topic, max_rounds)
    └── current_speaker = "optimist"

debate_graph.astream(state, stream_mode="messages")
    └── optimist_node → skeptic_node → optimist_node → ... → END
        └── metadata["langgraph_node"] 提供發言者資訊
```

### 環境變數

| 變數              | 預設值  | 說明                           |
| ----------------- | ------- | ------------------------------ |
| `USE_LANGGRAPH`   | `true`  | 啟用 LangGraph StateGraph 模式 |
| `USE_FAKE_STREAM` | `false` | 強制使用假資料模式             |

---

## 🔮 驗證結果

### Token 串流測試 ✅ 已通過

**測試結果**：

1. ✅ tokens 逐一推送（每個事件 1-3 字元，打字機效果）
2. ✅ `metadata["langgraph_node"]` 正確提供發言者
3. ✅ 輪次計算正確（無 off-by-one）

**測試輸出**（2 輪辯論）：

```
optimist: 第 1 輪 → skeptic: 第 1 輪 → optimist: 第 2 輪 → skeptic: 第 2 輪
Final round_count: 2
```

**結論**：`stream_mode="messages"` + `ainvoke` 在 ChatGroq（streaming=True）下可正常攔截 token 串流。

---

## 📊 專案進度

| 階段                       | 狀態      | 完成度 |
| -------------------------- | --------- | ------ |
| Phase 0（基礎架構）        | ✅ 完成   | 100%   |
| Phase 1（雲端部署）        | ✅ 完成   | 100%   |
| Phase 2（AI 辯論）         | ✅ 完成   | 100%   |
| Phase 3a（LangGraph 遷移） | ✅ 完成   | 100%   |
| Phase 3b（搜尋工具）       | 🔜 待開始 | 0%     |

---

**備註**：今天把架構改成 LangGraph 了！等驗證 token 串流效果後，如果正常就可以進入 Phase 3b 加入搜尋工具。
