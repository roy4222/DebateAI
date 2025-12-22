"""
Supabase Client Singleton

提供 Supabase 客戶端的單例模式，避免重複建立連線。
使用 SUPABASE_SERVICE_ROLE_KEY 繞過 RLS 進行寫入操作。
"""

from supabase import create_client, Client
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """
    取得 Supabase 客戶端單例
    
    Returns:
        Client: Supabase 客戶端實例
        
    Raises:
        ValueError: 如果環境變數未設定
    """
    global _supabase_client
    
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError(
                "Supabase 未設定。請設定 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY 環境變數。"
            )
        
        _supabase_client = create_client(url, key)
        logger.info("Supabase 客戶端已初始化")
    
    return _supabase_client


def is_supabase_enabled() -> bool:
    """
    檢查 Supabase 是否已設定
    
    Returns:
        bool: True 如果環境變數已設定
    """
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    return bool(url and key and len(url) > 10 and len(key) > 10)


def reset_client() -> None:
    """
    重置客戶端（主要用於測試）
    """
    global _supabase_client
    _supabase_client = None
