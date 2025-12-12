"""
DebateAI Backend - FastAPI 應用

Phase 3a: LangGraph StateGraph 串流
- langgraph_debate_stream() 使用 debate_graph.astream(stream_mode="messages")
- USE_LANGGRAPH 環境變數控制是否使用 LangGraph（預設 true）
- 保留 real_debate_stream() 作為回退方案（USE_LANGGRAPH=false）
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
import json
import re
import os

# 載入環境變數
load_dotenv()

app = FastAPI(title="DebateAI API", version="0.3.0")


# ============================================================
# 環境變數
# ============================================================
USE_FAKE_STREAM = os.getenv("USE_FAKE_STREAM", "false").lower() == "true"
USE_LANGGRAPH = os.getenv("USE_LANGGRAPH", "true").lower() == "true"  # Phase 3a: 預設使用 LangGraph
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
    topic: str
    max_rounds: int = 3


# ============================================================
# SSE 輔助函數
# ============================================================
def sse_event(data: dict) -> str:
    """生成 SSE 事件格式"""
    return f"data: {json.dumps(data)}\n\n"


# ============================================================
# Fake SSE 串流（Fallback）
# ============================================================
async def fake_debate_stream(topic: str, max_rounds: int = 3):
    """Phase 1 測試用：模擬 AI 辯論"""
    
    yield sse_event({'type': 'status', 'text': '⚡ [FAKE MODE] 正在喚醒模擬引擎...'})
    await asyncio.sleep(0.3)
    
    yield sse_event({'type': 'status', 'text': '🔥 模擬引擎已就緒！'})
    
    for round_num in range(1, max_rounds + 1):
        # Optimist
        yield sse_event({'type': 'speaker', 'node': 'optimist', 'text': f'第 {round_num} 輪'})
        
        optimist_text = f"關於「{topic}」，我認為這是充滿機會的！科技進步總是帶來新的可能性。"
        for char in optimist_text:
            yield sse_event({'type': 'token', 'node': 'optimist', 'text': char})
            await asyncio.sleep(0.02)
        
        yield sse_event({'type': 'speaker_end', 'node': 'optimist'})
        
        # Skeptic
        yield sse_event({'type': 'speaker', 'node': 'skeptic', 'text': f'第 {round_num} 輪'})
        
        skeptic_text = f"然而，我們必須謹慎看待「{topic}」。盲目樂觀可能導致忽視風險。"
        for char in skeptic_text:
            yield sse_event({'type': 'token', 'node': 'skeptic', 'text': char})
            await asyncio.sleep(0.02)
        
        yield sse_event({'type': 'speaker_end', 'node': 'skeptic'})
    
    yield sse_event({'type': 'complete', 'text': f'✅ [FAKE] 辯論結束！共 {max_rounds} 輪。'})


# ============================================================
# 真實 LLM 串流
# ============================================================
async def real_debate_stream(topic: str, max_rounds: int = 3):
    """Phase 2: 真正的 Token-Level 串流"""
    from app.graph import (
        get_llm, 
        create_initial_state, 
        build_prompt, 
        update_state_after_speaker
    )
    
    yield sse_event({'type': 'status', 'text': '⚡ 正在喚醒 AI 辯論引擎...'})
    
    # 初始化
    state = create_initial_state(topic, max_rounds)
    
    try:
        llm = get_llm()
        yield sse_event({'type': 'status', 'text': f'🔥 使用模型: {GROQ_MODEL}'})
    except Exception as e:
        yield sse_event({'type': 'error', 'text': f'LLM 初始化失敗: {str(e)}'})
        return
    
    # 辯論循環
    while state['current_speaker'] != 'end':
        speaker = state['current_speaker']
        round_num = state['round_count'] + 1
        
        # 發送 speaker 開始事件
        yield sse_event({'type': 'speaker', 'node': speaker, 'text': f'第 {round_num} 輪'})
        
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
            yield sse_event({'type': 'error', 'text': f'LLM 串流中斷: {str(e)}'})
            yield sse_event({'type': 'speaker_end', 'node': speaker})
            yield sse_event({'type': 'complete', 'text': '❌ 辯論因錯誤而中斷'})
            return
        
        # 發送 speaker 結束事件
        yield sse_event({'type': 'speaker_end', 'node': speaker})
        
        # 更新狀態
        if full_content:
            state = update_state_after_speaker(state, speaker, full_content)
        else:
            yield sse_event({'type': 'error', 'text': 'LLM 返回空回應'})
            break
    
    rounds_completed = state['round_count']
    yield sse_event({'type': 'complete', 'text': f'✅ 辯論完成！共進行了 {rounds_completed} 輪精彩交鋒。'})


# ============================================================
# LangGraph StateGraph 串流（Phase 3a）
# ============================================================
async def langgraph_debate_stream(topic: str, max_rounds: int = 3):
    """Phase 3a: 使用 LangGraph StateGraph 串流
    
    ⚠️ 關鍵驗證點：
    1. tokens 是否逐一推送（打字機效果）
    2. metadata["langgraph_node"] 是否正確提供發言者資訊
    3. 輪次計算是否正確（無 off-by-one）
    """
    from app.graph import debate_graph, create_initial_state
    
    yield sse_event({'type': 'status', 'text': '⚡ 正在喚醒 AI 辯論引擎...'})
    yield sse_event({'type': 'status', 'text': f'🔥 使用模型: {GROQ_MODEL} (LangGraph)'})
    
    state = create_initial_state(topic, max_rounds)
    
    current_node = None
    round_count = 0  # 獨立追蹤輪次，skeptic 發言結束時 +1
    
    try:
        async for message, metadata in debate_graph.astream(
            state,
            stream_mode="messages"
        ):
            # ⚠️ 防呆：metadata["langgraph_node"] 可能為 None
            node = metadata.get("langgraph_node") if metadata else None
            if not node:
                continue  # 跳過無效事件
            
            # 節點切換時發送 speaker 事件
            if node != current_node:
                # 結束前一個節點
                if current_node:
                    yield sse_event({'type': 'speaker_end', 'node': current_node})
                    # Skeptic 發言結束後才增加輪數
                    if current_node == "skeptic":
                        round_count += 1
                
                current_node = node
                
                # 計算顯示用輪次（optimist 開場時為第 1 輪）
                display_round = round_count + 1
                yield sse_event({
                    'type': 'speaker',
                    'node': node,
                    'text': f'第 {display_round} 輪'
                })
            
            # Token 串流
            if hasattr(message, 'content') and message.content:
                yield sse_event({
                    'type': 'token',
                    'node': node,
                    'text': message.content
                })
        
        # 最後一個節點結束
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


# ============================================================
# SSE 串流接口
# ============================================================
@app.post("/debate")
async def start_debate(req: DebateRequest):
    """啟動 AI 辯論串流
    
    串流模式選擇：
    1. USE_FAKE_STREAM=true 或無 GROQ_API_KEY → fake_debate_stream
    2. USE_LANGGRAPH=true（預設）→ langgraph_debate_stream（Phase 3a）
    3. USE_LANGGRAPH=false → real_debate_stream（Phase 2 回退）
    """
    
    if USE_FAKE_STREAM or not HAS_GROQ_KEY:
        stream_generator = fake_debate_stream(req.topic, req.max_rounds)
    elif USE_LANGGRAPH:
        stream_generator = langgraph_debate_stream(req.topic, req.max_rounds)
    else:
        stream_generator = real_debate_stream(req.topic, req.max_rounds)
    
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
        "version": "0.3.0",
        "phase": "3a",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "0.3.0",
        "phase": "3a",
        "has_groq_key": HAS_GROQ_KEY,
        "use_fake_stream": USE_FAKE_STREAM,
        "use_langgraph": USE_LANGGRAPH,
        "model": GROQ_MODEL if HAS_GROQ_KEY else None,
        "note": "Phase 3a: Using LangGraph StateGraph for debate flow control"
    }
