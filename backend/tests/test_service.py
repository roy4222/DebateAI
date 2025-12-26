"""
Debate Service Tests

測試 app/services/debate_service.py 的 CRUD 操作
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone

from app.services.debate_service import (
    serialize_message,
    serialize_messages,
    save_debate,
    get_recent_debates,
    get_debate_by_id,
    get_debates_paginated,
)


# ============================================================
# Message Serialization Tests
# ============================================================

class TestSerializeMessage:
    """serialize_message 單元測試"""
    
    def test_serialize_optimist_message(self):
        """樂觀者訊息序列化"""
        msg = {"node": "optimist", "text": "這是樂觀的觀點", "roundInfo": "第 1 輪"}
        result = serialize_message(msg)
        
        assert result["version"] == 1
        assert result["type"] == "ai"
        assert result["node"] == "optimist"
        assert result["content"] == "這是樂觀的觀點"
        assert result["roundInfo"] == "第 1 輪"
        assert "timestamp" in result
    
    def test_serialize_skeptic_message(self):
        """懷疑者訊息序列化"""
        msg = {"node": "skeptic", "text": "這是懷疑的觀點"}
        result = serialize_message(msg)
        
        assert result["type"] == "ai"
        assert result["node"] == "skeptic"
    
    def test_serialize_moderator_message(self):
        """主持人訊息序列化"""
        msg = {"node": "moderator", "text": "### 總結"}
        result = serialize_message(msg)
        
        assert result["type"] == "ai"
        assert result["node"] == "moderator"
    
    def test_serialize_system_message(self):
        """系統訊息序列化"""
        msg = {"node": "system", "text": "辯論開始"}
        result = serialize_message(msg)
        
        assert result["type"] == "system"
        assert result["node"] is None  # system node 不保留
    
    def test_serialize_unknown_node(self):
        """未知節點序列化為 human"""
        msg = {"node": "unknown", "text": "測試"}
        result = serialize_message(msg)
        
        assert result["type"] == "human"
        assert result["node"] is None


class TestSerializeMessages:
    """serialize_messages 批次測試"""
    
    def test_serialize_empty_list(self):
        """空列表序列化"""
        result = serialize_messages([])
        assert result == []
    
    def test_serialize_multiple_messages(self):
        """多個訊息序列化"""
        msgs = [
            {"node": "optimist", "text": "觀點 1"},
            {"node": "skeptic", "text": "反駁 1"},
        ]
        result = serialize_messages(msgs)
        
        assert len(result) == 2
        assert result[0]["node"] == "optimist"
        assert result[1]["node"] == "skeptic"


# ============================================================
# CRUD Tests
# ============================================================

class TestSaveDebate:
    """儲存辯論測試"""
    
    @pytest.mark.asyncio
    async def test_save_debate_success(self):
        """成功儲存辯論"""
        from app.services.debate_service import save_debate
        
        mock_result = MagicMock()
        mock_result.data = [{"id": "test-uuid"}]
        
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_table.insert.return_value.execute.return_value = mock_result
        mock_client.table.return_value = mock_table
        
        with patch("app.services.debate_service.is_supabase_enabled", return_value=True):
            with patch("app.services.debate_service.get_supabase", return_value=mock_client):
                result = await save_debate(
                    topic="測試主題",
                    messages=[{"node": "optimist", "text": "測試"}],
                    max_rounds=3,
                    rounds_completed=1
                )
        
        assert result == "test-uuid"
    
    @pytest.mark.asyncio
    async def test_save_debate_disabled(self):
        """Supabase 停用時返回 None"""
        from app.services.debate_service import save_debate
        
        with patch("app.services.debate_service.is_supabase_enabled", return_value=False):
            result = await save_debate(
                topic="測試主題",
                messages=[],
                max_rounds=3,
                rounds_completed=0
            )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_save_debate_error(self):
        """Supabase 錯誤時返回 None"""
        from app.services.debate_service import save_debate
        
        mock_client = MagicMock()
        mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
        
        with patch("app.services.debate_service.is_supabase_enabled", return_value=True):
            with patch("app.services.debate_service.get_supabase", return_value=mock_client):
                result = await save_debate(
                    topic="測試主題",
                    messages=[],
                    max_rounds=3,
                    rounds_completed=0
                )
        
        assert result is None


class TestGetRecentDebates:
    """get_recent_debates 測試"""
    
    @pytest.mark.asyncio
    async def test_get_recent_debates_success(self):
        """成功取得最近辯論"""
        from app.services.debate_service import get_recent_debates
        
        mock_result = MagicMock()
        mock_result.data = [{"id": "1", "topic": "測試主題"}]
        
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = mock_result
        
        with patch("app.services.debate_service.is_supabase_enabled", return_value=True):
            with patch("app.services.debate_service.get_supabase", return_value=mock_client):
                result = await get_recent_debates(limit=5)
        
        assert len(result) == 1
        assert result[0]["topic"] == "測試主題"
    
    @pytest.mark.asyncio
    async def test_get_recent_debates_disabled(self):
        """Supabase 停用時返回空列表"""
        from app.services.debate_service import get_recent_debates
        
        with patch("app.services.debate_service.is_supabase_enabled", return_value=False):
            result = await get_recent_debates()
        
        assert result == []


class TestGetDebateById:
    """get_debate_by_id 測試"""
    
    @pytest.mark.asyncio
    async def test_get_debate_by_id_success(self):
        """成功取得單一辯論"""
        from app.services.debate_service import get_debate_by_id
        
        mock_result = MagicMock()
        mock_result.data = {"id": "test-id", "topic": "測試主題", "messages": []}
        
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_result
        
        with patch("app.services.debate_service.is_supabase_enabled", return_value=True):
            with patch("app.services.debate_service.get_supabase", return_value=mock_client):
                result = await get_debate_by_id("test-id")
        
        assert result is not None
        assert result["topic"] == "測試主題"
    
    @pytest.mark.asyncio
    async def test_get_debate_by_id_not_found(self):
        """找不到辯論時返回 None"""
        from app.services.debate_service import get_debate_by_id
        
        mock_result = MagicMock()
        mock_result.data = None
        
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_result
        
        with patch("app.services.debate_service.is_supabase_enabled", return_value=True):
            with patch("app.services.debate_service.get_supabase", return_value=mock_client):
                result = await get_debate_by_id("nonexistent-id")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_debate_by_id_disabled(self):
        """Supabase 停用時返回 None"""
        from app.services.debate_service import get_debate_by_id
        
        with patch("app.services.debate_service.is_supabase_enabled", return_value=False):
            result = await get_debate_by_id("any-id")
        
        assert result is None


class TestGetDebatesPaginated:
    """get_debates_paginated 測試"""
    
    @pytest.mark.asyncio
    async def test_get_debates_paginated_page1(self):
        """取得第一頁"""
        from app.services.debate_service import get_debates_paginated
        
        mock_result = MagicMock()
        mock_result.data = [{"id": "1", "topic": "Topic 1"}]
        mock_result.count = 25
        
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.order.return_value.range.return_value.execute.return_value = mock_result
        
        with patch("app.services.debate_service.is_supabase_enabled", return_value=True):
            with patch("app.services.debate_service.get_supabase", return_value=mock_client):
                result = await get_debates_paginated(page=1, page_size=20)
        
        assert result["page"] == 1
        assert result["page_size"] == 20
    
    @pytest.mark.asyncio
    async def test_get_debates_paginated_disabled(self):
        """Supabase 停用時返回空結果"""
        from app.services.debate_service import get_debates_paginated
        
        with patch("app.services.debate_service.is_supabase_enabled", return_value=False):
            result = await get_debates_paginated()
        
        assert result["data"] == []
        assert result["total"] == 0
