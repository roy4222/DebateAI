"""
DebateAI - 辯論引擎狀態管理模組

職責：
- 狀態定義（DebateState）
- Prompt 生成（build_prompt）
- 狀態更新（update_state_after_speaker）

⚠️ 注意：目前不使用 LangGraph StateGraph
   LLM 串流由 main.py 直接控制以實現真正的 token-level 串流
   langgraph 依賴保留供 ChatGroq 使用，未來 Phase 3 可能重新引入
"""

from typing import TypedDict, Literal, List, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
import os


# ============================================================
# 狀態定義
# ============================================================
class DebateState(TypedDict):
    """辯論狀態"""
    messages: List[BaseMessage]  # 對話歷史
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
    """建立初始狀態"""
    return {
        "messages": [],
        "topic": topic,
        "current_speaker": "optimist",
        "round_count": 0,
        "max_rounds": max_rounds
    }
