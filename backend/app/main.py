"""
DebateAI Backend - FastAPI 應用

Phase 3c: LangGraph ToolNode 架構
- Agent 節點只負責決策，ToolNode 負責執行工具
- astream_events(version="v2") 可正確捕獲 on_tool_start/on_tool_end
- 修復搜尋指示器無法顯示的問題
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio
import json
import re
import os
import logging

# Phase 3c: 配置日誌
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

app = FastAPI(title="DebateAI API", version="0.4.0")


# ============================================================
# 環境變數
# ============================================================
USE_FAKE_STREAM = os.getenv("USE_FAKE_STREAM", "false").lower() == "true"
USE_LANGGRAPH = os.getenv("USE_LANGGRAPH", "true").lower() == "true"  # Phase 3b: 預設使用 LangGraph + astream_events
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HAS_GROQ_KEY = bool(GROQ_API_KEY and len(GROQ_API_KEY) > 10)
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


# ============================================================
# Regex CORS Middleware
# ============================================================
class RegexCORSMiddleware(CORSMiddleware):
    """支援 regex 匹配的 CORS Middleware"""
    def is_allowed_origin(self, origin: str) -> bool:
        if not origin:
            return False
        if origin.startswith("http://localhost"):
            return True
        if re.match(r"https://.*\.pages\.dev$", origin):
            return True
        if re.match(r"https://.*\.ggff\.net$", origin):
            return True
        allowed = os.getenv("ALLOWED_ORIGINS", "")
        if allowed and allowed != "*":
            allowed_list = [o.strip() for o in allowed.split(",") if o.strip()]
            if origin in allowed_list:
                return True
        return super().is_allowed_origin(origin)

app.add_middleware(
    RegexCORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True,
)


# ============================================================
# 請求模型
# ============================================================
class DebateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200, description="辯論主題，最多 200 字")
    max_rounds: int = Field(default=3, ge=1, le=5, description="辯論輪數，1-5 輪")
    language: str = Field(default="zh", pattern="^(zh|en)$", description="語言設定：zh (繁體中文) 或 en (English)")


# ============================================================
# SSE 輔助函數
# ============================================================
def sse_event(data: dict) -> str:
    """生成 SSE 事件格式"""
    return f"data: {json.dumps(data)}\n\n"


# ============================================================
# Fake SSE 串流（Fallback）
# ============================================================
async def fake_debate_stream(topic: str, max_rounds: int = 3, language: str = "zh"):
    """Phase 1 測試用：模擬 AI 辯論"""
    is_en = language == "en"

    msg_init = '⚡ [FAKE MODE] Waking up simulation engine...' if is_en else '⚡ [FAKE MODE] 正在喚醒模擬引擎...'
    msg_ready = '🔥 Simulation engine ready!' if is_en else '🔥 模擬引擎已就緒！'

    yield sse_event({'type': 'status', 'text': msg_init})
    await asyncio.sleep(0.3)

    yield sse_event({'type': 'status', 'text': msg_ready})
    
    for round_num in range(1, max_rounds + 1):
        # Optimist
        round_label = f'Round {round_num}' if is_en else f'第 {round_num} 輪'
        yield sse_event({'type': 'speaker', 'node': 'optimist', 'text': round_label})

        if is_en:
            optimist_text = f"Regarding '{topic}', I believe this is full of opportunities! Technological progress always brings new possibilities."
        else:
            optimist_text = f"關於「{topic}」，我認為這是充滿機會的！科技進步總是帶來新的可能性。"

        for char in optimist_text:
            yield sse_event({'type': 'token', 'node': 'optimist', 'text': char})
            await asyncio.sleep(0.02)

        yield sse_event({'type': 'speaker_end', 'node': 'optimist'})

        # Skeptic
        yield sse_event({'type': 'speaker', 'node': 'skeptic', 'text': round_label})

        if is_en:
            skeptic_text = f"However, we must be cautious about '{topic}'. Blind optimism may lead to overlooking risks."
        else:
            skeptic_text = f"然而，我們必須謹慎看待「{topic}」。盲目樂觀可能導致忽視風險。"

        for char in skeptic_text:
            yield sse_event({'type': 'token', 'node': 'skeptic', 'text': char})
            await asyncio.sleep(0.02)

        yield sse_event({'type': 'speaker_end', 'node': 'skeptic'})

    msg_complete = f'✅ [FAKE] Debate ended! {max_rounds} rounds.' if is_en else f'✅ [FAKE] 辯論結束！共 {max_rounds} 輪。'
    yield sse_event({'type': 'complete', 'text': msg_complete})


# ============================================================
# 真實 LLM 串流
# ============================================================
async def real_debate_stream(topic: str, max_rounds: int = 3, language: str = "zh"):
    """Phase 2: 真正的 Token-Level 串流"""
    from app.graph import (
        get_llm,
        create_initial_state,
        build_prompt,
        update_state_after_speaker
    )

    is_en = language == "en"

    # i18n 訊息
    msg_init = '⚡ Connecting to AI Debate Engine...' if is_en else '⚡ 正在喚醒 AI 辯論引擎...'
    msg_model = f'🔥 Using model: {GROQ_MODEL}' if is_en else f'🔥 使用模型: {GROQ_MODEL}'
    msg_llm_init_fail = 'LLM initialization failed: ' if is_en else 'LLM 初始化失敗: '
    msg_llm_stream_fail = 'LLM stream interrupted: ' if is_en else 'LLM 串流中斷: '
    msg_debate_error = '❌ Debate stopped due to error' if is_en else '❌ 辯論因錯誤而中斷'
    msg_empty_response = 'LLM returned empty response' if is_en else 'LLM 返回空回應'

    yield sse_event({'type': 'status', 'text': msg_init})

    # 初始化（language 已整合進 state）
    state = create_initial_state(topic, max_rounds, language)

    try:
        llm = get_llm()
        yield sse_event({'type': 'status', 'text': msg_model})
    except Exception as e:
        yield sse_event({'type': 'error', 'text': f'{msg_llm_init_fail}{str(e)}'})
        return

    # 辯論循環
    while state['current_speaker'] != 'end':
        speaker = state['current_speaker']
        round_num = state['round_count'] + 1

        # 發送 speaker 開始事件
        round_label = f'Round {round_num}' if is_en else f'第 {round_num} 輪'
        yield sse_event({'type': 'speaker', 'node': speaker, 'text': round_label})

        # 建構 prompt
        messages = build_prompt(state, speaker)

        # 直接呼叫 llm.astream() 實現 token 串流
        full_content = ""
        try:
            async for chunk in llm.astream(messages):
                if chunk.content:
                    full_content += chunk.content
                    yield sse_event({'type': 'token', 'node': speaker, 'text': chunk.content})
        except Exception as e:
            yield sse_event({'type': 'error', 'text': f'{msg_llm_stream_fail}{str(e)}'})
            yield sse_event({'type': 'speaker_end', 'node': speaker})
            yield sse_event({'type': 'complete', 'text': msg_debate_error})
            return

        # 發送 speaker 結束事件
        yield sse_event({'type': 'speaker_end', 'node': speaker})

        # 更新狀態
        if full_content:
            state = update_state_after_speaker(state, speaker, full_content)
        else:
            yield sse_event({'type': 'error', 'text': msg_empty_response})
            break

    rounds_completed = state['round_count']
    msg_complete = f'✅ Debate complete! {rounds_completed} exciting rounds.' if is_en else f'✅ 辯論完成！共進行了 {rounds_completed} 輪精彩交鋒。'
    yield sse_event({'type': 'complete', 'text': msg_complete})


# ============================================================
# LangGraph StateGraph 串流（Phase 3c - ToolNode 架構）
# ============================================================
async def langgraph_debate_stream(topic: str, max_rounds: int = 3, language: str = "zh"):
    """Phase 3c: 使用 ToolNode 實現工具事件追蹤
    
    架構改進：
    - Agent 節點只負責決策（返回 AIMessage，可能包含 tool_calls）
    - ToolNode 獨立執行工具，LangGraph 自動觸發 on_tool_start/on_tool_end
    - 修復搜尋指示器無法顯示的問題
    """
    from app.graph import debate_graph, create_initial_state

    logger.info(f"🌐 langgraph_debate_stream received language: {language}")
    is_en = language == "en"

    yield sse_event({'type': 'status', 'text': '⚡ ' + ('Connecting to AI Debate Engine...' if is_en else '正在喚醒 AI 辯論引擎...')})
    yield sse_event({'type': 'status', 'text': f'🔥 ' + ('Using model: ' if is_en else '使用模型: ') + f'{GROQ_MODEL} (LangGraph + Tools)'})

    # 初始化（language 已整合進 state）
    state = create_initial_state(topic, max_rounds, language)
    
    current_node = None
    round_count = 0
    current_tool_query = None
    
    try:
        async for event in debate_graph.astream_events(
            state,
            version="v2"
        ):
            event_type = event.get("event")
            event_name = event.get("name", "")
            event_tags = event.get("tags", [])
            
            # Phase 3c: 診斷日誌
            logger.debug(f"Event: type={event_type}, name={event_name}, tags={event_tags}")
            
            # 節點開始
            if event_type == "on_chain_start":
                name = event.get("name", "")
                # Phase 3d: 擴展支援 "moderator"
                if name in ("optimist", "skeptic", "moderator"):
                    if current_node and current_node != name:
                        yield sse_event({'type': 'speaker_end', 'node': current_node})
                        # ⚠️ 當 skeptic → moderator 時增加輪數（表示一輪完成）
                        if current_node == "skeptic" and name == "moderator":
                            round_count += 1
                    
                    current_node = name
                    
                    # 根據節點類型發送不同的 speaker 事件
                    if name == "moderator":
                        # Moderator 顯示特殊標記
                        moderator_text = 'Summary Report' if is_en else '總結報告'
                        yield sse_event({
                            'type': 'speaker',
                            'node': 'moderator',
                            'text': moderator_text
                        })
                    else:
                        # Optimist/Skeptic 顯示輪數
                        display_round = round_count + 1
                        round_text = f'Round {display_round}' if is_en else f'第 {display_round} 輪'
                        yield sse_event({
                            'type': 'speaker',
                            'node': name,
                            'text': round_text
                        })

            # 工具開始
            elif event_type == "on_tool_start":
                tool_input = event.get("data", {}).get("input", {})
                unknown_query = "Unknown query" if is_en else "未知查詢"
                query = tool_input.get("query", unknown_query) if isinstance(tool_input, dict) else str(tool_input)
                current_tool_query = query
                yield sse_event({
                    'type': 'tool_start',
                    'tool': 'web_search',
                    'query': query,
                    'node': current_node or "unknown"
                })
            
            # 工具結束（正常或錯誤）
            elif event_type in ("on_tool_end", "on_tool_error"):
                yield sse_event({
                    'type': 'tool_end',
                    'tool': 'web_search',
                    'node': current_node or "unknown"
                })
                current_tool_query = None
            
            # LLM Token 串流
            elif event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    # Phase 3d: 擴展支援 moderator
                    if current_node in ("optimist", "skeptic", "moderator"):
                        yield sse_event({
                            'type': 'token',
                            'node': current_node,
                            'text': chunk.content
                        })
        
        # 結束
        if current_node:
            yield sse_event({'type': 'speaker_end', 'node': current_node})

        msg_complete = f'✅ Debate complete! {round_count} exciting rounds.' if is_en else f'✅ 辯論完成！共進行了 {round_count} 輪精彩交鋒。'
        yield sse_event({
            'type': 'complete',
            'text': msg_complete
        })
    
    except Exception as e:
        # 確保工具指示器被清除
        if current_tool_query:
            yield sse_event({'type': 'tool_end', 'tool': 'web_search', 'node': current_node or "unknown"})
        msg_error = f'LangGraph error: {str(e)}' if is_en else f'LangGraph 錯誤: {str(e)}'
        yield sse_event({'type': 'error', 'text': msg_error})
        if current_node:
            yield sse_event({'type': 'speaker_end', 'node': current_node})


# ============================================================
# SSE 串流接口
# ============================================================
@app.post("/debate")
async def start_debate(req: DebateRequest):
    """啟動 AI 辯論串流
    
    串流模式選擇：
    1. USE_FAKE_STREAM=true 或無 GROQ_API_KEY → fake_debate_stream
    2. USE_LANGGRAPH=true（預設）→ langgraph_debate_stream（Phase 3b, astream_events）
    3. USE_LANGGRAPH=false → real_debate_stream（Phase 2 回退）
    """
    
    # Debug log
    logger.info(f"🚀 /debate API received: topic='{req.topic[:30]}...', max_rounds={req.max_rounds}, language={req.language}")
    
    if USE_FAKE_STREAM or not HAS_GROQ_KEY:
        stream_generator = fake_debate_stream(req.topic, req.max_rounds, req.language)
    elif USE_LANGGRAPH:
        stream_generator = langgraph_debate_stream(req.topic, req.max_rounds, req.language)
    else:
        stream_generator = real_debate_stream(req.topic, req.max_rounds, req.language)
    
    return StreamingResponse(
        stream_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ============================================================
# 基礎接口
# ============================================================
@app.get("/")
async def root():
    return {
        "message": "Welcome to DebateAI API 🎭",
        "version": "0.4.0",
        "phase": "4",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    from app.supabase_client import is_supabase_enabled
    return {
        "status": "healthy",
        "version": "0.4.0",
        "phase": "4",
        "has_groq_key": HAS_GROQ_KEY,
        "use_fake_stream": USE_FAKE_STREAM,
        "use_langgraph": USE_LANGGRAPH,
        "model": GROQ_MODEL if HAS_GROQ_KEY else None,
        "supabase_enabled": is_supabase_enabled(),
        "note": "Phase 4: Supabase debate history + i18n"
    }


# ============================================================
# Debate History Endpoints (Phase 4)
# ============================================================
class SaveDebateRequest(BaseModel):
    topic: str
    messages: list
    max_rounds: int = 3
    rounds_completed: int = 0


@app.post("/debate/save")
async def save_debate_endpoint(req: SaveDebateRequest):
    """儲存辯論到 Supabase"""
    from app.services.debate_service import save_debate
    
    debate_id = await save_debate(
        topic=req.topic,
        messages=req.messages,
        max_rounds=req.max_rounds,
        rounds_completed=req.rounds_completed
    )
    
    if debate_id:
        return {"success": True, "debate_id": debate_id}
    else:
        return {"success": False, "error": "Failed to save debate"}


@app.get("/debate/history")
async def get_history_endpoint(limit: int = 5):
    """取得最近辯論列表 (用於 sidebar)"""
    from app.services.debate_service import get_recent_debates
    
    debates = await get_recent_debates(limit=limit)
    return {"debates": debates}


@app.get("/debate/history/list")
async def get_history_paginated_endpoint(page: int = 1, page_size: int = 20):
    """分頁取得辯論列表"""
    from app.services.debate_service import get_debates_paginated
    
    result = await get_debates_paginated(page=page, page_size=page_size)
    return result


@app.get("/debate/history/{debate_id}")
async def get_debate_detail_endpoint(debate_id: str):
    """取得單一辯論詳細內容"""
    from app.services.debate_service import get_debate_by_id
    
    debate = await get_debate_by_id(debate_id)
    
    if debate:
        return debate
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Debate not found")
