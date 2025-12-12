# Phase 3b 實施計畫可行性分析：搜尋工具整合

## 📋 執行摘要

**結論：✅ 完全可行，Phase 3a 已成功實施**

評分：**9.5/10**

Phase 3a（LangGraph StateGraph 遷移）已成功完成：
- ✅ `debate_graph` 已成功編譯（CompiledStateGraph）
- ✅ `langgraph_debate_stream()` 已實施
- ✅ `USE_LANGGRAPH` 環境變數控制已就緒
- ✅ 保留 `real_debate_stream()` 作為回退方案

**現在可以安全地進入 Phase 3b：搜尋工具整合**

---

## 🎯 Phase 3b 目標

讓 AI Agent 能夠：
1. **自動判斷**何時需要搜尋資料
2. **執行搜尋**使用 Tavily（主）+ DuckDuckGo（備援）
3. **融入論述**將搜尋結果整合到辯論回應中
4. **視覺反饋**前端顯示「🔍 正在搜尋...」指示器

---

## 🔍 當前狀態檢查

### ✅ Phase 3a 驗證結果

**後端檔案**：
- `app/graph.py`: 234 行（含 StateGraph 定義）
- `app/main.py`: 309 行（含 `langgraph_debate_stream`）
- `debate_graph`: ✅ 成功編譯為 `CompiledStateGraph`

**架構特性**：
- ✅ 使用 `async def optimist_node` 和 `async def skeptic_node`
- ✅ 節點內使用 `await llm.ainvoke(messages)`
- ✅ `stream_mode="messages"` 串流機制
- ✅ `USE_LANGGRAPH` 環境變數控制（預設 true）

**缺失依賴**：
- ❌ `tavily-python` - Tavily API 客戶端
- ❌ `duckduckgo-search` - DuckDuckGo 搜尋工具

---

## 📝 Phase 3b 實施計畫

### 1. 後端變更

#### 步驟 1：安裝搜尋工具依賴

**檔案**：`backend/pyproject.toml`

```toml
[project]
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "python-dotenv>=1.0.0",
    "langchain>=0.3.0",
    "langchain-groq>=0.2.0",
    "langgraph>=1.0.0",
+   "tavily-python>=0.5.0",     # Phase 3b: 搜尋工具（主）
+   "duckduckgo-search>=6.0.0", # Phase 3b: 搜尋工具（備援）
]
```

**執行**：
```bash
cd backend
uv sync
```

---

#### 步驟 2：建立搜尋工具模組

**檔案**：`backend/app/tools/__init__.py`（新建）
```python
# 空檔案，標記為 Python package
```

**檔案**：`backend/app/tools/search.py`（新建）

```python
"""
DebateAI - 網路搜尋工具模組

三層容錯策略：
1. Tavily（主）- 專為 AI 設計，極度穩定
2. DuckDuckGo（備援）- 免費無限次數
3. 優雅降級 - 搜尋失敗不影響辯論
"""

from tavily import TavilyClient
from duckduckgo_search import DDGS
import os
import asyncio

# 初始化 Tavily 客戶端（可選）
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY")) if os.getenv("TAVILY_API_KEY") else None


async def tavily_search(query: str) -> dict:
    """第一層：Tavily 搜尋（專業 AI 搜尋）"""
    if not tavily_client:
        return {"success": False, "error": "No Tavily API key"}

    try:
        # Tavily 是同步的，用 asyncio 包裝
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: tavily_client.search(query, max_results=3, search_depth="basic")
        )

        results = response.get("results", [])
        if not results:
            return {"success": False, "error": "No results"}

        return {
            "success": True,
            "results": results,
            "source": "tavily"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def duckduckgo_search(query: str) -> dict:
    """第二層：DuckDuckGo 搜尋（免費備援）"""
    try:
        # DDGS 是同步的，用 asyncio 包裝
        loop = asyncio.get_event_loop()
        ddgs = DDGS()
        results = await loop.run_in_executor(
            None,
            lambda: list(ddgs.text(query, max_results=3))
        )

        if not results:
            return {"success": False, "error": "No results"}

        return {
            "success": True,
            "results": results,
            "source": "duckduckgo"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def web_search(query: str) -> dict:
    """三層容錯網路搜尋

    Args:
        query: 搜尋關鍵字

    Returns:
        dict: {
            "success": bool,
            "results": list,  # 搜尋結果（如果成功）
            "source": str,    # "tavily" | "duckduckgo" | "fallback"
            "formatted": str  # 格式化的結果文字
        }
    """

    # 第一層：Tavily
    result = await tavily_search(query)
    if result["success"]:
        formatted = format_results(result["results"], result["source"])
        return {**result, "formatted": formatted}

    # 第二層：DuckDuckGo
    result = await duckduckgo_search(query)
    if result["success"]:
        formatted = format_results(result["results"], result["source"])
        return {**result, "formatted": formatted}

    # 第三層：優雅降級
    return {
        "success": False,
        "source": "fallback",
        "formatted": f"[注意] 搜尋功能暫時無法使用，Agent 將基於現有知識回答關於「{query}」的問題。"
    }


def format_results(results: list, source: str) -> str:
    """格式化搜尋結果為可讀文字

    Args:
        results: 搜尋結果列表
        source: 來源（"tavily" | "duckduckgo"）

    Returns:
        格式化的文字
    """
    if source == "tavily":
        # Tavily 格式：{title, content, url}
        lines = [
            f"• {r.get('title', '未知標題')}: {r.get('content', '')[:200]}..."
            for r in results[:3]
        ]
    else:
        # DuckDuckGo 格式：{title, body, href}
        lines = [
            f"• {r.get('title', '未知標題')}: {r.get('body', '')[:200]}..."
            for r in results[:3]
        ]

    formatted = "\n".join(lines)
    return f"[{source.upper()}] 搜尋結果：\n{formatted}"
```

---

#### 步驟 3：定義 LangChain Tool

**檔案**：`backend/app/graph.py`

在文件開頭加入 imports：
```python
from langchain_core.tools import tool
```

在 `create_initial_state` 之後加入：

```python
# ============================================================
# 工具定義（Phase 3b）
# ============================================================

@tool
async def web_search_tool(query: str) -> str:
    """搜尋網路資料以獲取最新資訊、統計數據或事實。

    當需要以下情況時使用此工具：
    - 最新數據或統計資料
    - 具體事件的日期和細節
    - 科學研究結果
    - 市場趨勢或商業資訊

    Args:
        query: 搜尋關鍵字（簡潔明確）

    Returns:
        格式化的搜尋結果摘要
    """
    from app.tools.search import web_search

    result = await web_search(query)
    return result.get("formatted", "搜尋失敗")
```

---

#### 步驟 4：修改節點支援工具調用

**檔案**：`backend/app/graph.py`

修改 `get_llm()` 函數，新增可選的工具綁定：

```python
def get_llm(bind_tools: bool = False):
    """取得 LLM 實例

    Args:
        bind_tools: 是否綁定工具（Phase 3b）
    """
    model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    llm = ChatGroq(
        model=model_name,
        temperature=0.7,
        api_key=os.getenv("GROQ_API_KEY"),
        streaming=True
    )

    if bind_tools:
        return llm.bind_tools([web_search_tool])
    return llm
```

修改節點函數以處理工具調用：

```python
async def optimist_node(state: DebateState) -> dict:
    """樂觀者節點（支援工具調用）"""
    llm = get_llm(bind_tools=True)  # Phase 3b: 綁定工具
    messages = build_prompt(state, "optimist")

    # 第一次調用（可能請求工具）
    response = await llm.ainvoke(messages)

    # 處理工具調用循環
    while hasattr(response, 'tool_calls') and response.tool_calls:
        # 將 AI 回應加入訊息
        messages.append(response)

        # 執行每個工具調用
        for tool_call in response.tool_calls:
            from langchain_core.messages import ToolMessage

            # 執行工具（web_search_tool 是異步的）
            tool_result = await web_search_tool.ainvoke(tool_call["args"])

            # 將工具結果加入訊息
            messages.append(ToolMessage(
                content=tool_result,
                tool_call_id=tool_call["id"],
                name="web_search_tool"
            ))

        # 用工具結果重新調用 LLM
        response = await llm.ainvoke(messages)

    return {
        "messages": [AIMessage(content=response.content, name="optimist")],
        "current_speaker": "skeptic"
    }


async def skeptic_node(state: DebateState) -> dict:
    """懷疑者節點（支援工具調用）"""
    llm = get_llm(bind_tools=True)  # Phase 3b: 綁定工具
    messages = build_prompt(state, "skeptic")

    # 第一次調用
    response = await llm.ainvoke(messages)

    # 處理工具調用循環（同 optimist_node）
    while hasattr(response, 'tool_calls') and response.tool_calls:
        messages.append(response)

        for tool_call in response.tool_calls:
            from langchain_core.messages import ToolMessage
            tool_result = await web_search_tool.ainvoke(tool_call["args"])
            messages.append(ToolMessage(
                content=tool_result,
                tool_call_id=tool_call["id"],
                name="web_search_tool"
            ))

        response = await llm.ainvoke(messages)

    new_round = state["round_count"] + 1
    next_speaker = "end" if new_round >= state["max_rounds"] else "optimist"

    return {
        "messages": [AIMessage(content=response.content, name="skeptic")],
        "current_speaker": next_speaker,
        "round_count": new_round
    }
```

---

#### 步驟 5：更新 System Prompts

**檔案**：`backend/app/graph.py`

```python
OPTIMIST_SYSTEM = """你是一位充滿說服力的「樂觀辯手」。

規則：
1. 每次回應限 2-3 句話，簡短有力
2. 強調機會、優勢、正面影響
3. 如果對手提出質疑，必須正面反擊
4. 禁止說「你說得對」「我同意」等退讓語句
5. 使用繁體中文回應
6. **如果需要數據或事實支持論點，請使用 web_search_tool 查詢**

可用工具：
- web_search_tool(query: str): 搜尋最新資訊、統計數據或事實
"""

SKEPTIC_SYSTEM = """你是一位邏輯嚴謹的「懷疑辯手」。

規則：
1. 每次回應限 2-3 句話，直擊要害
2. 指出風險、漏洞、被忽視的代價
3. 質疑對手的樂觀假設，要求提出證據
4. 禁止認同對方觀點，保持批判立場
5. 使用繁體中文回應
6. **如果需要查證對手的論點，請使用 web_search_tool**

可用工具：
- web_search_tool(query: str): 搜尋最新資訊以查證論點
"""
```

---

#### 步驟 6：main.py 加入工具事件

**檔案**：`backend/app/main.py`

修改 `langgraph_debate_stream()` 以偵測工具調用：

```python
async def langgraph_debate_stream(topic: str, max_rounds: int = 3):
    """Phase 3a/3b: 使用 LangGraph StateGraph 串流（支援工具）"""
    from app.graph import debate_graph, create_initial_state

    yield sse_event({'type': 'status', 'text': '⚡ 正在喚醒 AI 辯論引擎...'})
    yield sse_event({'type': 'status', 'text': f'🔥 使用模型: {GROQ_MODEL} (LangGraph + Tools)'})

    state = create_initial_state(topic, max_rounds)

    current_node = None
    round_count = 0

    try:
        async for message, metadata in debate_graph.astream(
            state,
            stream_mode="messages"
        ):
            node = metadata.get("langgraph_node") if metadata else None
            if not node:
                continue

            # 節點切換
            if node != current_node:
                if current_node:
                    yield sse_event({'type': 'speaker_end', 'node': current_node})
                    if current_node == "skeptic":
                        round_count += 1

                current_node = node
                display_round = round_count + 1
                yield sse_event({
                    'type': 'speaker',
                    'node': node,
                    'text': f'第 {display_round} 輪'
                })

            # ⚠️ 新增：偵測工具調用
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    query = tool_call.get("args", {}).get("query", "未知查詢")
                    yield sse_event({
                        'type': 'tool_start',
                        'tool': 'web_search',
                        'query': query,
                        'node': node
                    })

            # ⚠️ 新增：偵測工具結果
            if message.__class__.__name__ == 'ToolMessage':
                # 工具執行完成
                yield sse_event({
                    'type': 'tool_end',
                    'tool': 'web_search',
                    'node': node
                })

            # Token 串流
            if hasattr(message, 'content') and message.content:
                yield sse_event({
                    'type': 'token',
                    'node': node,
                    'text': message.content
                })

        # 結束
        if current_node:
            yield sse_event({'type': 'speaker_end', 'node': current_node})
            if current_node == "skeptic":
                round_count += 1

        yield sse_event({
            'type': 'complete',
            'text': f'✅ 辯論完成！共進行了 {round_count} 輪精彩交鋒。'
        })

    except Exception as e:
        yield sse_event({'type': 'error', 'text': f'LangGraph 錯誤: {str(e)}'})
        if current_node:
            yield sse_event({'type': 'speaker_end', 'node': current_node})
```

---

### 2. 前端變更

#### 步驟 7：更新 TypeScript 類型

**檔案**：`frontend/app/lib/api.ts`

```typescript
export type SSEEvent =
    | { type: 'status'; text: string }
    | { type: 'speaker'; node: 'optimist' | 'skeptic'; text: string }
    | { type: 'token'; node: 'optimist' | 'skeptic'; text: string }
    | { type: 'speaker_end'; node: 'optimist' | 'skeptic' }
    | { type: 'tool_start'; tool: string; query: string; node: string }  // Phase 3b
    | { type: 'tool_end'; tool: string; node: string }                   // Phase 3b
    | { type: 'complete'; text: string }
    | { type: 'error'; text: string };
```

---

#### 步驟 8：前端顯示搜尋指示器

**檔案**：`frontend/app/components/DebateUI.tsx`

在 state 中加入：

```typescript
const [searchStatus, setSearchStatus] = useState<{
  isSearching: boolean;
  query?: string;
  node?: string;
}>({ isSearching: false });
```

在 `handleSSEEvent` 中處理：

```typescript
case "tool_start":
  setSearchStatus({
    isSearching: true,
    query: event.query,
    node: event.node
  });
  setStatus(`🔍 ${event.node === 'optimist' ? '樂觀者' : '懷疑者'}正在搜尋：${event.query}`);
  break;

case "tool_end":
  setSearchStatus({ isSearching: false });
  setStatus('✅ 搜尋完成，繼續辯論...');
  break;
```

在 UI 中顯示：

```tsx
{searchStatus.isSearching && (
  <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-800 rounded-lg flex items-center gap-3">
    <svg className="animate-spin h-5 w-5 text-yellow-600" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
    </svg>
    <div className="flex-1">
      <p className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
        🔍 正在搜尋資料...
      </p>
      <p className="text-xs text-yellow-700 dark:text-yellow-300">
        {searchStatus.query}
      </p>
    </div>
  </div>
)}
```

---

### 3. 環境變數配置

**檔案**：`backend/.env`（本地開發）

```bash
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.1-8b-instant
USE_LANGGRAPH=true
TAVILY_API_KEY=tvly_your_key_here  # Phase 3b: 可選，無則跳過 Tavily
```

**Cloud Run 部署**：

```bash
gcloud run deploy debate-api \
  --source . \
  --region asia-east1 \
  --set-env-vars GROQ_API_KEY=${GROQ_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY}
```

---

## ✅ 驗收標準

| 項目 | 預期結果 | 驗證方法 |
|------|---------|---------|
| Agent 自動判斷 | ✅ 需要數據時自動調用 web_search_tool | 主題：「2024年全球AI投資金額」|
| 搜尋狀態顯示 | ✅ 前端顯示「🔍 正在搜尋...」| 觀察 UI |
| Tavily 搜尋 | ✅ TAVILY_API_KEY 存在時使用 Tavily | 檢查日誌 |
| DuckDuckGo 備援 | ✅ Tavily 失敗時自動降級 | 測試錯誤 API Key |
| 優雅降級 | ✅ 兩者都失敗時辯論繼續 | 斷網測試 |
| 結果融入論述 | ✅ Agent 回應包含搜尋資料 | 檢查回應內容 |

---

## ⚠️ 風險評估

| 風險 | 影響 | 可能性 | 緩解措施 |
|------|------|--------|---------|
| Agent 過度調用工具 | 中 | 中 | Prompt 強調「僅需要時」搜尋 |
| 搜尋延遲（3-5秒）| 低 | 高 | 顯示搜尋指示器 |
| Tavily 配額用盡 | 低 | 低 | DuckDuckGo 自動備援 |
| 工具循環無限 | 高 | 低 | 限制 max iterations（LangGraph 內建）|
| Token 串流中斷 | 中 | 低 | 工具調用在 ainvoke 內完成 |

---

## ⏱️ 時間估計

| 任務 | 預計時間 | 備註 |
|------|---------|------|
| 安裝依賴 | 5 分鐘 | `uv sync` |
| 建立 search.py | 20-25 分鐘 | 三層容錯邏輯 |
| 修改 graph.py（工具定義 + 節點）| 30-35 分鐘 | 最複雜部分 |
| 修改 main.py（SSE 事件）| 15-20 分鐘 | 偵測工具調用 |
| 前端 UI 更新 | 20-25 分鐘 | 搜尋指示器 |
| 本地測試 | 15-20 分鐘 | 功能 + 容錯 |
| 部署驗證 | 10-15 分鐘 | 生產環境 |
| **總計** | **115-145 分鐘** | **約 2-2.5 小時** |

---

## 📌 實施順序

### Day 1（建議一次完成）

1. **後端搜尋工具**（45-50 分鐘）
   - 安裝依賴
   - 建立 `app/tools/search.py`
   - 定義 `@tool web_search_tool`

2. **後端節點修改**（45-50 分鐘）
   - 修改 `get_llm()` 支援 `bind_tools`
   - 修改 `optimist_node` 和 `skeptic_node` 處理工具循環
   - 更新 System Prompts
   - 修改 `main.py` 偵測工具事件

3. **前端 UI**（20-25 分鐘）
   - 更新 TypeScript 類型
   - 加入搜尋狀態指示器

4. **測試部署**（20-30 分鐘）
   - 本地測試（功能 + 容錯）
   - 部署到 Cloud Run

---

## 🎯 關鍵成功因素

1. **工具循環處理正確**
   - 必須用 `while` 循環處理多次工具調用
   - 每次都要將 `ToolMessage` 加回 messages

2. **異步處理一致**
   - `web_search_tool` 必須是 async
   - Tavily/DDGS 同步調用需用 `run_in_executor`

3. **Prompt 設計**
   - 明確告知何時使用工具
   - 強調「僅需要時」避免過度調用

4. **錯誤處理完善**
   - 搜尋失敗不影響辯論
   - 優雅降級訊息清晰

---

## 📋 最終檢查清單

### 開始前
- [ ] Phase 3a 已成功部署並測試
- [ ] 確認 `debate_graph` 正常運作
- [ ] 確認 token streaming 有效

### 實施中
- [ ] `pyproject.toml` 加入依賴
- [ ] 建立 `app/tools/` 目錄
- [ ] 實作三層容錯搜尋
- [ ] 定義 `@tool` 裝飾器
- [ ] 修改節點處理工具循環
- [ ] 更新 System Prompts
- [ ] 前端加入搜尋指示器

### 測試
- [ ] 本地測試 Tavily 搜尋
- [ ] 測試 DuckDuckGo 備援
- [ ] 測試優雅降級
- [ ] 驗證搜尋結果融入論述
- [ ] 檢查前端 UI 指示器

### 部署
- [ ] 設定 TAVILY_API_KEY 環境變數
- [ ] 部署到 Cloud Run
- [ ] 生產環境測試

---

## 🔗 參考資料

- [LangChain Tools Documentation](https://python.langchain.com/docs/modules/agents/tools/)
- [Tavily API Documentation](https://docs.tavily.com/)
- [DuckDuckGo Search Documentation](https://pypi.org/project/duckduckgo-search/)
- [LangGraph Tool Calling](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)

---

## ✅ 結論

**Phase 3b 計畫完全可行**，並且在 Phase 3a 成功的基礎上，實施風險更低。

**推薦立即開始實施**，預計 2-2.5 小時可完成並部署。
