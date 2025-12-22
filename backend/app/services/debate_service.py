"""
Debate Service Layer

負責辯論歷史的 CRUD 操作和訊息序列化。
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging

from app.supabase_client import get_supabase, is_supabase_enabled

logger = logging.getLogger(__name__)

# ============================================================
# Message Schema v1
# ============================================================
# {
#   "version": 1,
#   "type": "ai" | "human" | "system" | "tool",
#   "node": "optimist" | "skeptic" | "moderator" | null,
#   "content": "message text",
#   "roundInfo": "第 1 輪",  # optional
#   "timestamp": "2025-12-22T14:30:00Z"
# }


def serialize_message(msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    將前端訊息格式轉換為 StoredMessage 格式 (v1)
    
    Args:
        msg: 前端訊息 {node, text, roundInfo?}
        
    Returns:
        StoredMessage 格式的字典
    """
    node = msg.get("node")
    
    # 根據 node 決定 type
    if node in ("optimist", "skeptic", "moderator"):
        msg_type = "ai"
    elif node == "system":
        msg_type = "system"
    else:
        msg_type = "human"
    
    return {
        "version": 1,
        "type": msg_type,
        "node": node if node in ("optimist", "skeptic", "moderator") else None,
        "content": msg.get("text", ""),
        "roundInfo": msg.get("roundInfo"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def serialize_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    批次序列化訊息列表
    """
    return [serialize_message(msg) for msg in messages]


# ============================================================
# CRUD Operations
# ============================================================

async def save_debate(
    topic: str,
    messages: List[Dict[str, Any]],
    max_rounds: int = 3,
    rounds_completed: int = 0
) -> Optional[str]:
    """
    儲存辯論到資料庫
    
    Args:
        topic: 辯論主題
        messages: 訊息列表 (前端格式)
        max_rounds: 最大輪數
        rounds_completed: 完成輪數
        
    Returns:
        辯論 UUID，失敗返回 None
    """
    if not is_supabase_enabled():
        logger.warning("Supabase 未設定，跳過儲存")
        return None
    
    try:
        supabase = get_supabase()
        
        # 序列化訊息
        stored_messages = serialize_messages(messages)
        
        # 插入資料
        result = supabase.table("debate_history").insert({
            "topic": topic,
            "messages": stored_messages,
            "max_rounds": max_rounds,
            "rounds_completed": rounds_completed,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        
        if result.data and len(result.data) > 0:
            debate_id = result.data[0].get("id")
            logger.info(f"辯論已儲存: {debate_id}")
            return debate_id
        
        return None
        
    except Exception as e:
        logger.error(f"儲存辯論失敗: {e}")
        return None


async def get_recent_debates(limit: int = 5) -> List[Dict[str, Any]]:
    """
    取得最近的辯論列表 (用於 sidebar)
    
    Args:
        limit: 最大筆數
        
    Returns:
        辯論摘要列表 [{id, topic, created_at, rounds_completed}]
    """
    if not is_supabase_enabled():
        return []
    
    try:
        supabase = get_supabase()
        
        result = supabase.table("debate_history") \
            .select("id, topic, created_at, rounds_completed") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"取得最近辯論失敗: {e}")
        return []


async def get_debate_by_id(debate_id: str) -> Optional[Dict[str, Any]]:
    """
    取得單一辯論詳細內容
    
    Args:
        debate_id: 辯論 UUID
        
    Returns:
        辯論詳細資料，或 None
    """
    if not is_supabase_enabled():
        return None
    
    try:
        supabase = get_supabase()
        
        result = supabase.table("debate_history") \
            .select("*") \
            .eq("id", debate_id) \
            .single() \
            .execute()
        
        return result.data
        
    except Exception as e:
        logger.error(f"取得辯論失敗: {e}")
        return None


async def get_debates_paginated(
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """
    分頁取得辯論列表
    
    Args:
        page: 頁碼 (1-indexed)
        page_size: 每頁筆數
        
    Returns:
        {data, total, page, page_size}
    """
    if not is_supabase_enabled():
        return {"data": [], "total": 0, "page": page, "page_size": page_size}
    
    try:
        supabase = get_supabase()
        
        # 計算 offset
        offset = (page - 1) * page_size
        
        # 取得資料
        result = supabase.table("debate_history") \
            .select("id, topic, created_at, rounds_completed, max_rounds", count="exact") \
            .order("created_at", desc=True) \
            .range(offset, offset + page_size - 1) \
            .execute()
        
        return {
            "data": result.data or [],
            "total": result.count or 0,
            "page": page,
            "page_size": page_size,
        }
        
    except Exception as e:
        logger.error(f"分頁取得辯論失敗: {e}")
        return {"data": [], "total": 0, "page": page, "page_size": page_size}
