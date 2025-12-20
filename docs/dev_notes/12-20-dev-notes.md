# 📅 開發日記：DebateAI - 12/20

**日期**：2025-12-20  
**狀態**：✅ Phase 3c 完成 - ToolNode 架構重構  
**版本**：0.3.3

---

## 🎉 今日成就 (Highlights)

### Phase 3c：ToolNode 架構重構 ✅

| 檔案       | 變更內容                                                              |
| ---------- | --------------------------------------------------------------------- |
| `graph.py` | 引入 ToolNode、新增 `tool_callback_node`、重構 Agent 節點為僅決策模式 |
| `main.py`  | 添加診斷日誌、版本更新至 0.3.3                                        |

### 架構對比

```
Phase 3b (舊)：
optimist_node → 內部手動調用 web_search_tool.ainvoke() → skeptic_node
                        ↑ LangGraph 無法追蹤事件 ❌

Phase 3c (新)：
optimist_node → [has tool_calls?] → ToolNode → tool_callback → optimist_node
                       ↓ no                      ↑ LangGraph 自動追蹤 ✅
                  skeptic_node
```

---

## 🔧 今日解決的問題

| #   | 問題                                 | 根因                                       | 解決方案                            |
| --- | ------------------------------------ | ------------------------------------------ | ----------------------------------- |
| 1   | 搜尋指示器永遠不顯示                 | 工具在節點內部手動調用，LangGraph 無法追蹤 | 使用 ToolNode 獨立執行工具          |
| 2   | 第一輪辯論者偶爾無輸出               | on_chain_start 事件識別問題                | 添加診斷日誌 + 狀態追蹤             |
| 3   | 工具返回後 Prompt 重複 SystemMessage | `messages[-6:]` 可能包含 SystemMessage     | 只取非 SystemMessage 的訊息         |
| 4   | 版本號不一致                         | Phase 3c 應為 0.3.3                        | 統一更新所有版本引用                |
| 5   | 條件邊缺少容錯路由                   | tool_callback 可能意外成為 current_speaker | 添加 tool_callback 到所有條件邊     |
| 6   | 使用字串比較 `__class__.__name__`    | 不夠 Pythonic                              | 改用 `isinstance(msg, ToolMessage)` |

---

## 📝 關鍵技術變更

### 1. DebateState 擴展

```python
class DebateState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    topic: str
    current_speaker: Literal["optimist", "skeptic", "tools", "tool_callback", "end"]
    round_count: int
    max_rounds: int
    tool_iterations: int  # 新增：工具迭代計數器
    last_agent: Literal["optimist", "skeptic", ""]  # 新增：記錄上一個 Agent
```

### 2. Agent 節點簡化

```python
async def optimist_node(state: DebateState) -> dict:
    # 只負責決策，不執行工具
    response = await llm.ainvoke(prompt_messages)

    if has_tool_calls:
        return {"messages": [response], "current_speaker": "tools", "last_agent": "optimist"}
    else:
        return {"messages": [final_response], "current_speaker": "skeptic"}
```

### 3. ToolNode 自動管理

```python
from langgraph.prebuilt import ToolNode

tool_node = ToolNode([web_search_tool])
_graph.add_node("tools", tool_node)
```

### 4. 工具回調節點

```python
async def tool_callback_node(state: DebateState) -> dict:
    iterations = state.get("tool_iterations", 0) + 1
    if iterations >= MAX_TOOL_ITERATIONS:
        return {"current_speaker": last_agent, "tool_iterations": 0}
    return {"current_speaker": last_agent, "tool_iterations": iterations}
```

---

## 📊 專案進度

| 階段                       | 狀態      | 完成度 |
| -------------------------- | --------- | ------ |
| Phase 0（基礎架構）        | ✅ 完成   | 100%   |
| Phase 1（雲端部署）        | ✅ 完成   | 100%   |
| Phase 2（AI 辯論）         | ✅ 完成   | 100%   |
| Phase 3a（LangGraph 遷移） | ✅ 完成   | 100%   |
| Phase 3b（搜尋工具）       | ✅ 完成   | 100%   |
| Phase 3c（ToolNode 重構）  | ✅ 完成   | 100%   |
| Phase 3d（Moderator）      | 🔜 待開始 | 0%     |

---

## ✅ 驗證結果

- ✅ 搜尋指示器正常顯示「🔍 正在搜尋資料...」
- ✅ 第一輪辯論者正常輸出
- ✅ 工具事件 (on_tool_start/on_tool_end) 正確觸發
- ✅ `/health` 返回 Phase 3c v0.3.3

---

## 📌 下一步

1. Phase 3d：Moderator Agent（總結報告）
2. 添加搜尋來源連結顯示
3. 改進搜尋進度顯示（如「找到 3 個網站」）
4. 部署 Phase 3c 到生產環境
