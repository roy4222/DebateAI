"""
DebateAI - 辯論引擎狀態管理模組

Phase 3c: 使用 LangGraph ToolNode 實現工具調用事件追蹤
- Agent 節點只負責決策（返回 AIMessage，可能包含 tool_calls）
- ToolNode 獨立執行工具（LangGraph 自動追蹤 on_tool_start/on_tool_end）
- 條件邊控制流程
"""

from typing import TypedDict, Literal, List, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
import os
import logging

logger = logging.getLogger(__name__)


# ============================================================
# 狀態定義（Phase 3c）
# ============================================================
class DebateState(TypedDict):
    """辯論狀態
    
    ⚠️ messages 使用 add_messages 註解，LangGraph 會自動合併新舊訊息
    ⚠️ current_speaker 新增 "tools" 和 "tool_callback" 選項
    """
    messages: Annotated[List[BaseMessage], add_messages]
    topic: str
    current_speaker: Literal["optimist", "skeptic", "tools", "tool_callback", "end"]
    round_count: int
    max_rounds: int
    tool_iterations: int  # Phase 3c: 工具迭代計數器
    last_agent: Literal["optimist", "skeptic", ""]  # Phase 3c: 記錄上一個 Agent


# ============================================================
# System Prompts
# ============================================================
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


# ============================================================
# 工具定義（Phase 3b/3c）
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
    
    logger.debug(f"web_search_tool called with query: {query}")
    result = await web_search(query)
    return result.get("formatted", "搜尋失敗")


# 工具列表（用於 ToolNode）
tools = [web_search_tool]


# ============================================================
# LLM 工廠
# ============================================================
def get_llm(bind_tools: bool = False):
    """取得 LLM 實例

    Args:
        bind_tools: 是否綁定工具（Phase 3c）
    """
    model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    llm = ChatGroq(
        model=model_name,
        temperature=0.7,
        api_key=os.getenv("GROQ_API_KEY"),
        streaming=True
    )

    if bind_tools:
        return llm.bind_tools(tools)
    return llm


# ============================================================
# 輔助函數
# ============================================================
def format_messages(messages: List[BaseMessage], limit: int = 4) -> str:
    """格式化最近的訊息歷史"""
    recent = messages[-limit:] if len(messages) > limit else messages
    lines = []
    for m in recent:
        name = getattr(m, 'name', None) or m.__class__.__name__
        if hasattr(m, 'content') and m.content:
            lines.append(f"[{name}]: {m.content}")
    return "\n".join(lines) if lines else "(尚無對話)"


def build_prompt(state: DebateState, speaker: str) -> List[BaseMessage]:
    """為指定發言者建構 prompt（只用於首次調用）"""
    history = format_messages(state['messages'])
    round_num = state['round_count'] + 1
    
    if speaker == "optimist":
        system = OPTIMIST_SYSTEM
        if state['round_count'] == 0 and len(state['messages']) == 0:
            user_content = f"""辯論主題：{state['topic']}

開場白，請以樂觀者身份發言。"""
        else:
            user_content = f"""辯論主題：{state['topic']}

第 {round_num} 輪，請以樂觀者身份發言。

對話歷史：
{history}"""
    else:  # skeptic
        system = SKEPTIC_SYSTEM
        user_content = f"""辯論主題：{state['topic']}

第 {round_num} 輪，請以懷疑者身份反駁樂觀者的論點。

對話歷史：
{history}"""
    
    return [
        SystemMessage(content=system),
        HumanMessage(content=user_content)
    ]


def update_state_after_speaker(state: DebateState, speaker: str, content: str) -> DebateState:
    """發言結束後更新狀態（保留供 real_debate_stream 使用）"""
    new_messages = state['messages'] + [AIMessage(content=content, name=speaker)]
    
    if speaker == "optimist":
        return {
            **state,
            "messages": new_messages,
            "current_speaker": "skeptic"
        }
    else:
        new_round = state['round_count'] + 1
        next_speaker = "end" if new_round >= state['max_rounds'] else "optimist"
        return {
            **state,
            "messages": new_messages,
            "current_speaker": next_speaker,
            "round_count": new_round
        }


def create_initial_state(topic: str, max_rounds: int = 3) -> DebateState:
    """建立初始狀態（Phase 3c）"""
    return {
        "messages": [],
        "topic": topic,
        "current_speaker": "optimist",
        "round_count": 0,
        "max_rounds": max_rounds,
        "tool_iterations": 0,
        "last_agent": ""
    }


# ============================================================
# LangGraph StateGraph（Phase 3c - ToolNode 架構）
# ============================================================

MAX_TOOL_ITERATIONS = 3


async def optimist_node(state: DebateState) -> dict:
    """樂觀者節點（Phase 3c: 僅決策，不執行工具）
    
    返回的 AIMessage 可能包含 tool_calls，由條件邊決定下一步
    """
    logger.debug("optimist_node: entering")
    
    # 檢查是否已達到工具迭代上限
    tool_iterations = state.get('tool_iterations', 0)
    should_bind_tools = tool_iterations < MAX_TOOL_ITERATIONS
    
    llm = get_llm(bind_tools=should_bind_tools)
    logger.debug(f"optimist_node: tool_iterations={tool_iterations}, bind_tools={should_bind_tools}")
    
    # 檢查是否從工具回調返回（messages 中有 ToolMessage）
    messages = state.get('messages', [])
    if messages and isinstance(messages[-1], ToolMessage):
        # 從工具返回：提取工具結果作為文字
        tool_results = []
        for msg in reversed(messages[-6:]):
            if isinstance(msg, ToolMessage):
                tool_results.insert(0, f"[搜尋結果]: {msg.content}")
        
        tool_context = "\n".join(tool_results) if tool_results else ""
        history = format_messages(messages)
        
        prompt_messages = [
            SystemMessage(content=OPTIMIST_SYSTEM),
            HumanMessage(content=f"""辯論主題：{state['topic']}

{tool_context}

請根據以上搜尋結果，以樂觀者身份繼續發言。（請直接發言，不要再搜尋）

對話歷史：
{history}""")
        ]
    else:
        # 首次調用
        prompt_messages = build_prompt(state, "optimist")
    
    response = await llm.ainvoke(prompt_messages)
    logger.debug(f"optimist_node: response has tool_calls={bool(getattr(response, 'tool_calls', None))}")
    
    # 檢查是否有工具調用
    has_tool_calls = hasattr(response, 'tool_calls') and response.tool_calls
    
    if has_tool_calls:
        # ℹ️ Groq 要求所有 AIMessage 都有 name 屬性
        response_with_name = AIMessage(
            content=response.content or "",
            tool_calls=response.tool_calls,
            name="optimist"
        )
        return {
            "messages": [response_with_name],
            "current_speaker": "tools",
            "last_agent": "optimist"
        }
    else:
        # 確保 content 有 name 屬性
        final_response = AIMessage(content=response.content or "(無回應)", name="optimist")
        return {
            "messages": [final_response],
            "current_speaker": "skeptic",
            "last_agent": "optimist",
            "tool_iterations": 0  # 重置
        }


async def skeptic_node(state: DebateState) -> dict:
    """懷疑者節點（Phase 3c: 僅決策，不執行工具）"""
    logger.debug("skeptic_node: entering")
    
    # 檢查是否已達到工具迭代上限
    tool_iterations = state.get('tool_iterations', 0)
    should_bind_tools = tool_iterations < MAX_TOOL_ITERATIONS
    
    llm = get_llm(bind_tools=should_bind_tools)
    logger.debug(f"skeptic_node: tool_iterations={tool_iterations}, bind_tools={should_bind_tools}")
    
    messages = state.get('messages', [])
    if messages and isinstance(messages[-1], ToolMessage):
        # 從工具返回：提取工具結果作為文字
        tool_results = []
        for msg in reversed(messages[-6:]):
            if isinstance(msg, ToolMessage):
                tool_results.insert(0, f"[搜尋結果]: {msg.content}")
        
        tool_context = "\n".join(tool_results) if tool_results else ""
        history = format_messages(messages)
        
        prompt_messages = [
            SystemMessage(content=SKEPTIC_SYSTEM),
            HumanMessage(content=f"""辯論主題：{state['topic']}

{tool_context}

請根據以上搜尋結果，以懷疑者身份繼續反駁。（請直接發言，不要再搜尋）

對話歷史：
{history}""")
        ]
    else:
        prompt_messages = build_prompt(state, "skeptic")
    
    response = await llm.ainvoke(prompt_messages)
    logger.debug(f"skeptic_node: response has tool_calls={bool(getattr(response, 'tool_calls', None))}")
    
    has_tool_calls = hasattr(response, 'tool_calls') and response.tool_calls
    
    if has_tool_calls:
        # ℹ️ Groq 要求所有 AIMessage 都有 name 屬性
        response_with_name = AIMessage(
            content=response.content or "",
            tool_calls=response.tool_calls,
            name="skeptic"
        )
        return {
            "messages": [response_with_name],
            "current_speaker": "tools",
            "last_agent": "skeptic"
        }
    else:
        new_round = state["round_count"] + 1
        next_speaker = "end" if new_round >= state["max_rounds"] else "optimist"
        final_response = AIMessage(content=response.content or "(無回應)", name="skeptic")
        return {
            "messages": [final_response],
            "current_speaker": next_speaker,
            "last_agent": "skeptic",
            "round_count": new_round,
            "tool_iterations": 0
        }


async def tool_callback_node(state: DebateState) -> dict:
    """工具執行後的回調節點
    
    決定返回哪個 Agent，並檢查迭代限制
    """
    logger.debug("tool_callback_node: entering")
    iterations = state.get("tool_iterations", 0) + 1
    last_agent = state.get("last_agent", "optimist")
    
    logger.debug(f"tool_callback_node: iterations={iterations}, last_agent={last_agent}")
    
    # 檢查是否超過限制
    if iterations >= MAX_TOOL_ITERATIONS:
        logger.warning(f"tool_callback_node: max iterations reached, forcing return to {last_agent}")
        return {
            "current_speaker": last_agent,
            "tool_iterations": 0
        }
    
    return {
        "current_speaker": last_agent,
        "tool_iterations": iterations
    }


def should_continue(state: DebateState) -> str:
    """路由函數：根據 current_speaker 決定下一個節點"""
    speaker = state.get("current_speaker", "end")
    logger.debug(f"should_continue: current_speaker={speaker}")
    return speaker


# ============================================================
# 建立 StateGraph（Phase 3c）
# ============================================================

# 建立 ToolNode
tool_node = ToolNode(tools)

# 建立 StateGraph
_graph = StateGraph(DebateState)

# 添加節點
_graph.add_node("optimist", optimist_node)
_graph.add_node("skeptic", skeptic_node)
_graph.add_node("tools", tool_node)
_graph.add_node("tool_callback", tool_callback_node)

# 設定入口點
_graph.set_conditional_entry_point(
    should_continue,
    {
        "optimist": "optimist",
        "skeptic": "skeptic",
        "tools": "tools",
        "end": END
    }
)

# Optimist 後的路由
_graph.add_conditional_edges(
    "optimist",
    should_continue,
    {
        "tools": "tools",
        "skeptic": "skeptic",
        "tool_callback": "tool_callback",  # 容錯路由
        "end": END
    }
)

# Skeptic 後的路由
_graph.add_conditional_edges(
    "skeptic",
    should_continue,
    {
        "tools": "tools",
        "optimist": "optimist",
        "tool_callback": "tool_callback",  # 容錯路由
        "end": END
    }
)

# Tool 執行後進入回調
_graph.add_edge("tools", "tool_callback")

# Tool 回調後返回 Agent
_graph.add_conditional_edges(
    "tool_callback",
    should_continue,
    {
        "optimist": "optimist",
        "skeptic": "skeptic",
        "end": END
    }
)

# 編譯為可執行的 graph
debate_graph = _graph.compile()

logger.info("debate_graph compiled successfully (Phase 3c: ToolNode architecture)")
