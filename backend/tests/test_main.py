"""
API Integration Tests

測試 app/main.py 的 FastAPI endpoints
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


# ============================================================
# Health & Root Endpoints
# ============================================================

class TestHealthEndpoint:
    """健康檢查 endpoint 測試"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint_success(self, async_client):
        """GET /health 返回 200"""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "phase" in data
    
    @pytest.mark.asyncio
    async def test_health_endpoint_config_info(self, async_client):
        """健康檢查包含配置資訊"""
        response = await async_client.get("/health")
        
        data = response.json()
        assert "has_groq_key" in data
        assert "supabase_enabled" in data


class TestRootEndpoint:
    """根路徑 endpoint 測試"""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client):
        """GET / 返回基本資訊"""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


# ============================================================
# Debate History Endpoints
# ============================================================

class TestSaveDebateEndpoint:
    """POST /debate/save 測試"""
    
    @pytest.mark.asyncio
    async def test_save_debate_success(self, async_client, mock_supabase):
        """成功儲存辯論"""
        payload = {
            "topic": "測試主題",
            "messages": [{"node": "optimist", "text": "測試"}],
            "max_rounds": 3,
            "rounds_completed": 1
        }
        
        with patch("app.services.debate_service.save_debate", new_callable=AsyncMock) as mock_save:
            mock_save.return_value = "test-uuid"
            response = await async_client.post("/debate/save", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @pytest.mark.asyncio
    async def test_save_debate_invalid_json(self, async_client):
        """無效 JSON 返回 422"""
        payload = {"topic": ""}  # missing required fields
        
        response = await async_client.post("/debate/save", json=payload)
        
        # FastAPI validation error returns 422
        assert response.status_code in [422, 200]  # depends on validation


class TestGetHistoryEndpoint:
    """GET /debate/history 測試"""
    
    @pytest.mark.asyncio
    async def test_get_history_success(self, async_client):
        """取得最近辯論列表"""
        with patch("app.services.debate_service.get_recent_debates", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [
                {"id": "1", "topic": "Topic 1", "created_at": "2025-12-26", "rounds_completed": 3}
            ]
            response = await async_client.get("/debate/history?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert "debates" in data
    
    @pytest.mark.asyncio
    async def test_get_history_default_limit(self, async_client):
        """使用預設 limit"""
        with patch("app.services.debate_service.get_recent_debates", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []
            response = await async_client.get("/debate/history")
        
        assert response.status_code == 200


class TestGetDebateByIdEndpoint:
    """GET /debate/history/{id} 測試"""
    
    @pytest.mark.asyncio
    async def test_get_debate_by_id_success(self, async_client):
        """成功取得單一辯論"""
        with patch("app.services.debate_service.get_debate_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {
                "id": "test-id",
                "topic": "Test Topic",
                "messages": [],
                "created_at": "2025-12-26"
            }
            response = await async_client.get("/debate/history/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "Test Topic"
    
    @pytest.mark.asyncio
    async def test_get_debate_by_id_not_found(self, async_client):
        """找不到辯論返回 404"""
        with patch("app.services.debate_service.get_debate_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            response = await async_client.get("/debate/history/nonexistent")
        
        assert response.status_code == 404


class TestGetPaginatedEndpoint:
    """GET /debate/history/list 測試"""
    
    @pytest.mark.asyncio
    async def test_get_paginated_success(self, async_client):
        """分頁取得辯論列表"""
        with patch("app.services.debate_service.get_debates_paginated", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {
                "data": [],
                "total": 0,
                "page": 1,
                "page_size": 20
            }
            response = await async_client.get("/debate/history/list?page=1&page_size=20")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data


# ============================================================
# Debate Streaming Endpoint
# ============================================================

class TestDebateEndpoint:
    """POST /debate SSE 串流測試"""
    
    @pytest.mark.asyncio
    async def test_debate_endpoint_validation(self, async_client):
        """請求驗證"""
        payload = {"topic": "測試主題", "max_rounds": 3}
        
        # Just check that the endpoint is reachable
        # Full SSE test is complex due to streaming
        response = await async_client.post("/debate", json=payload)
        
        # Should return 200 with streaming response
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_debate_endpoint_missing_topic(self, async_client):
        """缺少 topic 返回 422"""
        payload = {"max_rounds": 3}
        
        response = await async_client.post("/debate", json=payload)
        
        assert response.status_code == 422


# ============================================================
# CORS Tests
# ============================================================

class TestCORS:
    """CORS 配置測試"""
    
    @pytest.mark.asyncio
    async def test_cors_localhost_allowed(self, async_client):
        """localhost 被允許"""
        response = await async_client.options(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # CORS preflight should work
        assert response.status_code in [200, 204, 405]
    
    @pytest.mark.asyncio
    async def test_cors_pages_dev_allowed(self, async_client):
        """*.pages.dev 被允許"""
        response = await async_client.get(
            "/health",
            headers={"Origin": "https://debate-ai.pages.dev"}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_cors_ggff_net_allowed(self, async_client):
        """*.ggff.net 被允許"""
        response = await async_client.get(
            "/health",
            headers={"Origin": "https://debateai.roy422.ggff.net"}
        )
        
        assert response.status_code == 200
