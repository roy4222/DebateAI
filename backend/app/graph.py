"""
DebateAI - 辯論引擎狀態管理模組

職責：
- 狀態定義（DebateState）
- Prompt 生成（build_prompt）
- LangGraph StateGraph 節點與路由

Phase 3a: 使用 LangGraph StateGraph 管理辯論流程
- optimist_node / skeptic_node 異步節點
- debate_graph.astream(state, stream_mode="messages") 進行串流
"""

from typing import TypedDict, Literal, List, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import os


# ============================================================
# 狀態定義
# ============================================================
class DebateState(TypedDict):
    """辯論狀態
    
    ⚠️ messages 使用 add_messages 註解，LangGraph 會自動合併新舊訊息
    """
    messages: Annotated[List[BaseMessage], add_messages]  # 自動累積訊息
    topic: str                   # 辯論主題
    current_speaker: Literal["optimist", "skeptic", "end"]  # 下一位發言者
    round_count: int             # 當前輪數（Skeptic 發言後 +1）
    max_rounds: int              # 最大輪數


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
"""

SKEPTIC_SYSTEM = """你是一位邏輯嚴謹的「懷疑辯手」。

規則：
1. 每次回應限 2-3 句話，直擊要害
2. 指出風險、漏洞、被忽視的代價
3. 質疑對手的樂觀假設，要求提出證據
4. 禁止認同對方觀點，保持批判立場
5. 使用繁體中文回應
"""


# ============================================================
# LLM 工廠
# ============================================================
def get_llm() -> ChatGroq:
    """取得 LLM 實例"""
    model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    return ChatGroq(
        model=model_name,
        temperature=0.7,
        api_key=os.getenv("GROQ_API_KEY"),
        streaming=True
    )


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
    """為指定發言者建構 prompt"""
    history = format_messages(state['messages'])
    round_num = state['round_count'] + 1  # 顯示用，從 1 開始
    
    if speaker == "optimist":
        system = OPTIMIST_SYSTEM
        if state['round_count'] == 0:
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
    """發言結束後更新狀態"""
    new_messages = state['messages'] + [AIMessage(content=content, name=speaker)]
    
    if speaker == "optimist":
        # Optimist 說完，換 Skeptic
        return {
            **state,
            "messages": new_messages,
            "current_speaker": "skeptic"
        }
    else:
        # Skeptic 說完，round_count += 1，判斷是否結束
        new_round = state['round_count'] + 1
        next_speaker = "end" if new_round >= state['max_rounds'] else "optimist"
        return {
            **state,
            "messages": new_messages,
            "current_speaker": next_speaker,
            "round_count": new_round
        }


def create_initial_state(topic: str, max_rounds: int) -> DebateState:
    """建立初始狀態
    
    ⚠️ current_speaker 必須與入口點對齊（預設 optimist）
    """
    return {
        "messages": [],
        "topic": topic,
        "current_speaker": "optimist",
        "round_count": 0,
        "max_rounds": max_rounds
    }


# ============================================================
# LangGraph StateGraph（Phase 3a）
# ============================================================

async def optimist_node(state: DebateState) -> dict:
    """樂觀者節點
    
    ⚠️ 使用 ainvoke 讓 stream_mode="messages" 攔截 tokens
    ⚠️ topic/max_rounds 不需返回（StateGraph 會保留未變更的欄位）
    ⚠️ messages 使用 add_messages 註解，只需返回新訊息
    """
    llm = get_llm()
    messages = build_prompt(state, "optimist")
    response = await llm.ainvoke(messages)
    
    return {
        "messages": [AIMessage(content=response.content, name="optimist")],
        "current_speaker": "skeptic"
    }


async def skeptic_node(state: DebateState) -> dict:
    """懷疑者節點
    
    ⚠️ Skeptic 發言後 round_count += 1
    ⚠️ 達到 max_rounds 時設定 current_speaker = "end"
    """
    llm = get_llm()
    messages = build_prompt(state, "skeptic")
    response = await llm.ainvoke(messages)
    
    new_round = state["round_count"] + 1
    next_speaker = "end" if new_round >= state["max_rounds"] else "optimist"
    
    return {
        "messages": [AIMessage(content=response.content, name="skeptic")],
        "current_speaker": next_speaker,
        "round_count": new_round
    }


def should_continue(state: DebateState) -> str:
    """路由函數：根據 current_speaker 決定下一個節點"""
    return state["current_speaker"]


# 建立 StateGraph
_graph = StateGraph(DebateState)
_graph.add_node("optimist", optimist_node)
_graph.add_node("skeptic", skeptic_node)

# 設定入口點（根據初始 current_speaker 決定）
_graph.set_conditional_entry_point(
    should_continue,
    {
        "optimist": "optimist",
        "skeptic": "skeptic",
        "end": END
    }
)

# 設定邊（每個節點結束後根據 current_speaker 決定）
_graph.add_conditional_edges(
    "optimist",
    should_continue,
    {"skeptic": "skeptic", "end": END}
)

_graph.add_conditional_edges(
    "skeptic",
    should_continue,
    {"optimist": "optimist", "end": END}
)

# 編譯為可執行的 graph
debate_graph = _graph.compile()
