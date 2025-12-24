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
    current_speaker: Literal["optimist", "skeptic", "tools", "tool_callback", "moderator", "end"]
    round_count: int
    max_rounds: int
    tool_iterations: int  # Phase 3c: 工具迭代計數器
    last_agent: Literal["optimist", "skeptic", ""]  # Phase 3c: 記錄上一個 Agent


# ============================================================
# 語言設定
# ============================================================
current_language = "zh"  # 預設繁體中文

def set_language(lang: str):
    """設定語言：'zh' (繁體中文) 或 'en' (English)"""
    global current_language
    current_language = lang if lang in ("zh", "en") else "zh"
    logger.info(f"🌐 Language set to: {current_language}")

def get_language() -> str:
    """取得當前語言設定"""
    return current_language


# ============================================================
# System Prompts - 中文版
# ============================================================
OPTIMIST_SYSTEM_ZH = """你是一位充滿說服力的「樂觀辯手」。

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

SKEPTIC_SYSTEM_ZH = """你是一位邏輯嚴謹的「懷疑辯手」。

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

MODERATOR_ROUND_SUMMARY_ZH = """你是一位中立的辯論主持人。
請針對本輪辯論做簡短總結（80-120字）：

格式：
### 🔄 第 {round} 輪小結
**樂觀者**: [核心論點 1 句話]
**懷疑者**: [核心論點 1 句話]
**分歧點**: [本輪最主要的爭議 1 句話]

規則：
1. 使用繁體中文
2. 保持絕對中立
3. 簡潔有力，不超過 120 字
"""

MODERATOR_FINAL_SUMMARY_ZH = """你是一位中立、客觀的辯論主持人。
請根據完整辯論生成最終總結報告（200-300字）：

格式：
## 📊 辯論總結報告

### 🟢 樂觀者核心論點
- [論點 1]
- [論點 2]

### 🔴 懷疑者核心論點
- [論點 1]
- [論點 2]

### ⚖️ 關鍵分歧點
[雙方最主要的分歧是什麼？1-2 句話]

### 💡 綜合評估
[客觀分析雙方論證的優劣，指出哪些論點更有說服力，2-3 句話]

### 🎯 結論建議
[給讀者的實用建議，1 句話]

規則：
1. 使用繁體中文
2. 保持中立客觀
3. 總字數 200-300 字
"""


# ============================================================
# System Prompts - 英文版
# ============================================================
OPTIMIST_SYSTEM_EN = """You are a persuasive "Optimist Debater".

**IMPORTANT: You MUST respond in English only, regardless of the topic's language.**

Rules:
1. Keep responses to 2-3 sentences, short and powerful
2. Emphasize opportunities, advantages, and positive impacts
3. If challenged, respond with strong counter-arguments
4. Never say "you're right" or "I agree" - no concessions
5. **Always respond in English, even if the topic is in another language**
6. **Use web_search_tool to find data or facts to support your arguments**

Available tools:
- web_search_tool(query: str): Search for latest information, statistics, or facts
"""

SKEPTIC_SYSTEM_EN = """You are a logical "Skeptic Debater".

**IMPORTANT: You MUST respond in English only, regardless of the topic's language.**

Rules:
1. Keep responses to 2-3 sentences, hit the key points
2. Point out risks, flaws, and overlooked costs
3. Challenge opponent's optimistic assumptions, demand evidence
4. Never agree with opponent's view, maintain critical stance
5. **Always respond in English, even if the topic is in another language**
6. **Use web_search_tool to verify opponent's claims**

Available tools:
- web_search_tool(query: str): Search for latest information to verify claims
"""

MODERATOR_ROUND_SUMMARY_EN = """You are a neutral debate moderator.

**IMPORTANT: Respond in English only, even if the debate was in another language.**

Please provide a brief summary of this round (80-120 words):

Format:
### 🔄 Round {round} Summary
**Optimist**: [Core argument in 1 sentence]
**Skeptic**: [Core argument in 1 sentence]
**Key Disagreement**: [Main point of contention in 1 sentence]

Rules:
1. **Always respond in English**
2. Remain absolutely neutral
3. Be concise, no more than 120 words
"""

MODERATOR_FINAL_SUMMARY_EN = """You are a neutral, objective debate moderator.

**IMPORTANT: Respond in English only, even if the debate was in another language.**

Please generate a final summary report based on the complete debate (200-300 words):

Format:
## 📊 Debate Summary Report

### 🟢 Optimist's Core Arguments
- [Argument 1]
- [Argument 2]

### 🔴 Skeptic's Core Arguments
- [Argument 1]
- [Argument 2]

### ⚖️ Key Points of Disagreement
[What is the main disagreement between both sides? 1-2 sentences]

### 💡 Overall Assessment
[Objectively analyze the strengths and weaknesses of both sides' arguments, 2-3 sentences]

### 🎯 Conclusion & Recommendation
[Practical advice for the reader, 1 sentence]

Rules:
1. **Always respond in English**
2. Remain neutral and objective
3. Total word count 200-300 words
"""


# ============================================================
# 取得對應語言的 Prompt
# ============================================================
def get_optimist_system() -> str:
    logger.info(f"🌐 get_optimist_system: current_language={current_language}")
    return OPTIMIST_SYSTEM_EN if current_language == "en" else OPTIMIST_SYSTEM_ZH

def get_skeptic_system() -> str:
    logger.info(f"🌐 get_skeptic_system: current_language={current_language}")
    return SKEPTIC_SYSTEM_EN if current_language == "en" else SKEPTIC_SYSTEM_ZH

def get_moderator_round_summary(round_num: int) -> str:
    template = MODERATOR_ROUND_SUMMARY_EN if current_language == "en" else MODERATOR_ROUND_SUMMARY_ZH
    return template.format(round=round_num)

def get_moderator_final_summary() -> str:
    return MODERATOR_FINAL_SUMMARY_EN if current_language == "en" else MODERATOR_FINAL_SUMMARY_ZH


# ============================================================
# 工具定義（Phase 3b/3c）
# ============================================================

@tool
async def web_search_tool(query: str) -> str:
    """Search the web for latest information, statistics, or facts.

    Use this tool when you need:
    - Latest data or statistics
    - Specific event dates and details
    - Scientific research results
    - Market trends or business information

    Args:
        query: Search keywords (concise and clear)

    Returns:
        Formatted search results summary
    """
    from app.tools.search import web_search
    
    logger.debug(f"web_search_tool called with query: {query}")
    result = await web_search(query, language=current_language)
    
    # 根據語言返回不同的錯誤訊息
    fallback = "Search failed" if current_language == "en" else "搜尋失敗"
    return result.get("formatted", fallback)


# 工具列表（用於 ToolNode）
tools = [web_search_tool]


# ============================================================
# LLM 工廠（含 Rate Limit 模型切換）
# ============================================================

# 預設備用模型列表（按優先順序排列）
DEFAULT_FALLBACK_MODELS = [
    "moonshotai/kimi-k2-instruct-0905",  # Moonshot Kimi K2，高品質
    "llama-3.1-8b-instant",               # 高配額，快速
]


class RateLimitRetryLLM:
    """LLM 包裝器：遇到 429 限流時自動切換模型
    
    特點：
    - 維護一個「已限流」模型集合（cooldown_models）
    - 遇到 429 時，將當前模型加入 cooldown，切換到下一個可用模型重試
    - 所有模型都限流時，等待 retry-after 秒後重試主模型
    """
    
    # 類級別變數：追蹤全局限流狀態
    cooldown_models: set = set()
    
    def __init__(self, primary_model: str, fallback_models: list, bind_tools: bool = False):
        self.primary_model = primary_model
        self.fallback_models = fallback_models
        self.bind_tools = bind_tools
        self.api_key = os.getenv("GROQ_API_KEY")
        self._current_model = primary_model
        self._tools = tools if bind_tools else None
    
    def _get_available_model(self) -> str:
        """取得目前可用的模型（排除已限流的）"""
        all_models = [self.primary_model] + self.fallback_models
        for model in all_models:
            if model not in RateLimitRetryLLM.cooldown_models:
                return model
        # 所有模型都限流，返回主模型（會觸發等待）
        logger.warning("All models in cooldown, resetting and using primary model")
        RateLimitRetryLLM.cooldown_models.clear()
        return self.primary_model
    
    def _create_llm(self, model_name: str):
        """建立 ChatGroq 實例"""
        llm = ChatGroq(
            model=model_name,
            temperature=0.7,
            api_key=self.api_key,
            streaming=True
        )
        if self._tools:
            return llm.bind_tools(self._tools)
        return llm
    
    async def ainvoke(self, messages, **kwargs):
        """異步調用 LLM，遇到限流自動切換模型"""
        import asyncio
        
        max_retries = len(self.fallback_models) + 2  # 嘗試所有模型 + 額外重試
        last_error = None
        
        for attempt in range(max_retries):
            current_model = self._get_available_model()
            llm = self._create_llm(current_model)
            
            try:
                logger.debug(f"RateLimitRetryLLM: attempt {attempt + 1}, model={current_model}")
                response = await llm.ainvoke(messages, **kwargs)
                
                # 成功後，從 cooldown 移除此模型（如果之前被加入）
                RateLimitRetryLLM.cooldown_models.discard(current_model)
                self._current_model = current_model
                return response
                
            except Exception as e:
                error_str = str(e).lower()
                
                # 檢查是否為 429 限流錯誤
                if "429" in str(e) or "rate" in error_str or "too many" in error_str:
                    logger.warning(f"RateLimitRetryLLM: model {current_model} hit rate limit, switching...")
                    RateLimitRetryLLM.cooldown_models.add(current_model)
                    last_error = e
                    
                    # 如果還有其他模型可用，立即重試
                    if len(RateLimitRetryLLM.cooldown_models) < len(self.fallback_models) + 1:
                        continue
                    else:
                        # 所有模型都限流，等待一段時間後重置
                        logger.warning("All models rate limited, waiting 10 seconds...")
                        await asyncio.sleep(10)
                        RateLimitRetryLLM.cooldown_models.clear()
                        continue
                else:
                    # 非限流錯誤，直接拋出
                    raise
        
        # 所有重試都失敗
        raise last_error or Exception("All LLM retry attempts failed")
    
    @property
    def current_model(self) -> str:
        """返回當前使用的模型"""
        return self._current_model


def get_llm(bind_tools: bool = False):
    """取得 LLM 實例（含 Rate Limit 容錯）

    Args:
        bind_tools: 是否綁定工具（Phase 3c）
    
    環境變數：
        GROQ_MODEL: 主要模型（預設 llama-3.1-8b-instant）
        GROQ_FALLBACK_MODELS: 備用模型，逗號分隔（可選）
    """
    primary_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    # 解析備用模型列表
    fallback_env = os.getenv("GROQ_FALLBACK_MODELS", "")
    if fallback_env:
        fallback_models = [m.strip() for m in fallback_env.split(",") if m.strip()]
    else:
        # 使用預設列表，但排除主模型
        fallback_models = [m for m in DEFAULT_FALLBACK_MODELS if m != primary_model]
    
    logger.debug(f"get_llm: primary={primary_model}, fallbacks={fallback_models}, bind_tools={bind_tools}")
    
    return RateLimitRetryLLM(
        primary_model=primary_model,
        fallback_models=fallback_models,
        bind_tools=bind_tools
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
    
    if lines:
        return "\n".join(lines)
    else:
        return "(No conversation yet)" if current_language == "en" else "(尚無對話)"


def build_prompt(state: DebateState, speaker: str) -> List[BaseMessage]:
    """為指定發言者建構 prompt（只用於首次調用）"""
    history = format_messages(state['messages'])
    round_num = state['round_count'] + 1
    is_en = current_language == "en"
    
    # 語言指示（開頭和結尾）
    lang_start = "*** RESPOND IN ENGLISH ONLY ***\n\n" if is_en else ""
    lang_end = "\n\n*** IMPORTANT: Your response MUST be in English! ***" if is_en else ""
    
    if speaker == "optimist":
        system = get_optimist_system()
        if state['round_count'] == 0 and len(state['messages']) == 0:
            if is_en:
                user_content = f"""{lang_start}Debate Topic: {state['topic']}

Opening statement, please speak as the Optimist.{lang_end}"""
            else:
                user_content = f"""辯論主題：{state['topic']}

開場白，請以樂觀者身份發言。"""
        else:
            if is_en:
                user_content = f"""{lang_start}Debate Topic: {state['topic']}

Round {round_num}, please speak as the Optimist.

Conversation History:
{history}{lang_end}"""
            else:
                user_content = f"""辯論主題：{state['topic']}

第 {round_num} 輪，請以樂觀者身份發言。

對話歷史：
{history}"""
    else:  # skeptic
        system = get_skeptic_system()
        if is_en:
            user_content = f"""{lang_start}Debate Topic: {state['topic']}

Round {round_num}, please refute the Optimist's arguments as the Skeptic.

Conversation History:
{history}{lang_end}"""
        else:
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
    
    messages = state.get('messages', [])
    if messages and isinstance(messages[-1], ToolMessage):
        # 從工具返回：提取工具結果作為文字
        is_en = current_language == "en"
        tool_results = []
        for msg in reversed(messages[-6:]):
            if isinstance(msg, ToolMessage):
                prefix = "[Search Result]: " if is_en else "[搜尋結果]: "
                tool_results.insert(0, f"{prefix}{msg.content}")
        
        tool_context = "\n".join(tool_results) if tool_results else ""
        history = format_messages(messages)
        
        if is_en:
            user_prompt = f"""*** RESPOND IN ENGLISH ONLY ***

Debate Topic: {state['topic']}

{tool_context}

Based on the search results above, please continue speaking as the Optimist. (Please respond directly without searching again)

Conversation History:
{history}

*** IMPORTANT: Your response MUST be in English! ***"""
        else:
            user_prompt = f"""辯論主題：{state['topic']}

{tool_context}

請根據以上搜尋結果，以樂觀者身份繼續發言。（請直接發言，不要再搜尋）

對話歷史：
{history}"""
        
        prompt_messages = [
            SystemMessage(content=get_optimist_system()),
            HumanMessage(content=user_prompt)
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
        is_en = current_language == "en"
        tool_results = []
        for msg in reversed(messages[-6:]):
            if isinstance(msg, ToolMessage):
                prefix = "[Search Result]: " if is_en else "[搜尋結果]: "
                tool_results.insert(0, f"{prefix}{msg.content}")
        
        tool_context = "\n".join(tool_results) if tool_results else ""
        history = format_messages(messages)
        
        if is_en:
            user_prompt = f"""*** RESPOND IN ENGLISH ONLY ***

Debate Topic: {state['topic']}

{tool_context}

Based on the search results above, please continue refuting as the Skeptic. (Please respond directly without searching again)

Conversation History:
{history}

*** IMPORTANT: Your response MUST be in English! ***"""
        else:
            user_prompt = f"""辯論主題：{state['topic']}

{tool_context}

請根據以上搜尋結果，以懷疑者身份繼續反駁。（請直接發言，不要再搜尋）

對話歷史：
{history}"""
        
        prompt_messages = [
            SystemMessage(content=get_skeptic_system()),
            HumanMessage(content=user_prompt)
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
        # Phase 3d: 導向 Moderator（而非 Optimist 或 END）
        final_response = AIMessage(content=response.content or "(無回應)", name="skeptic")
        
        # ⚠️ 不再在此增加輪數，交由 Moderator 處理
        return {
            "messages": [final_response],
            "current_speaker": "moderator",
            "last_agent": "skeptic",
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
# Phase 3d: Moderator 節點
# ============================================================

async def moderator_node(state: DebateState) -> dict:
    """主持人節點：生成階段性或最終總結

    邏輯：
    - 輪次 < max_rounds: 階段性總結 → 返回 optimist
    - 輪次 = max_rounds: 最終總結 → 返回 end
    """
    logger.debug("moderator_node: entering")

    llm = get_llm(bind_tools=False)  # 不綁定工具

    current_round = state.get("round_count", 0) + 1  # Moderator 執行時還未 ++
    max_rounds = state.get("max_rounds", 3)
    is_final = (current_round >= max_rounds)

    # 選擇 Prompt
    is_en = current_language == "en"
    
    if is_final:
        system_prompt = get_moderator_final_summary()
        if is_en:
            prompt_context = f"""*** RESPOND IN ENGLISH ONLY ***

Debate Topic: {state['topic']}

Complete Debate Record:
{format_messages(state['messages'], limit=30)}

Please generate the final summary report.

*** IMPORTANT: Your response MUST be in English! ***"""
        else:
            prompt_context = f"""辯論主題：{state['topic']}

完整辯論記錄：
{format_messages(state['messages'], limit=30)}

請生成最終總結報告。"""
    else:
        system_prompt = get_moderator_round_summary(current_round)

        # ⚠️ 只提取本輪的 Optimist/Skeptic 對話（避免包含舊的 Moderator 總結）
        recent_debate_msgs = [
            m for m in state['messages'][-8:]
            if getattr(m, 'name', None) in ("optimist", "skeptic")
        ]

        if is_en:
            prompt_context = f"""*** RESPOND IN ENGLISH ONLY ***

Debate Topic: {state['topic']}

This Round's Dialogue:
{format_messages(recent_debate_msgs, limit=6)}

Please generate the Round {current_round} summary.

*** IMPORTANT: Your response MUST be in English! ***"""
        else:
            prompt_context = f"""辯論主題：{state['topic']}

本輪對話：
{format_messages(recent_debate_msgs, limit=6)}

請生成第 {current_round} 輪小結。"""

    prompt_messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt_context)
    ]

    response = await llm.ainvoke(prompt_messages)
    final_response = AIMessage(
        content=response.content or "(無法生成總結)",
        name="moderator"
    )

    # 決定下一步
    new_round = current_round  # Moderator 完成後才更新輪數
    next_speaker = "end" if is_final else "optimist"

    logger.debug(f"moderator_node: round={new_round}, next={next_speaker}")

    return {
        "messages": [final_response],
        "current_speaker": next_speaker,
        "round_count": new_round,  # ⚠️ 重要：Moderator 負責更新輪數
        "tool_iterations": 0  # 清零工具計數，讓下一輪可以使用工具
    }


# ============================================================
# 建立 StateGraph（Phase 3d）
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
_graph.add_node("moderator", moderator_node)  # Phase 3d: 新增

# 設定入口點
_graph.set_conditional_entry_point(
    should_continue,
    {
        "optimist": "optimist",
        "skeptic": "skeptic",
        "tools": "tools",
        "moderator": "moderator",  # Phase 3d: 新增
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
        "tool_callback": "tool_callback",
        "moderator": "moderator",  # Phase 3d: 容錯路由
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
        "tool_callback": "tool_callback",
        "moderator": "moderator",  # Phase 3d: 主要路由
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
        "moderator": "moderator",  # Phase 3d: 容錯路由
        "end": END
    }
)

# Moderator 後的路由（Phase 3d）
_graph.add_conditional_edges(
    "moderator",
    should_continue,
    {
        "optimist": "optimist",  # 未滿 3 輪，繼續辯論
        "end": END               # 已滿 3 輪，結束
    }
)

# 編譯為可執行的 graph
debate_graph = _graph.compile()

logger.info("debate_graph compiled successfully (Phase 3d: Moderator Agent)")

