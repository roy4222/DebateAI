"""
Search Tools Tests

測試 app/tools/search.py 的搜尋功能
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


# ============================================================
# Tavily Search Tests
# ============================================================

class TestTavilySearch:
    """Tavily 搜尋測試"""
    
    @pytest.mark.asyncio
    async def test_tavily_search_success(self):
        """Tavily 搜尋成功"""
        from app.tools.search import tavily_search
        
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {"title": "Result 1", "content": "Content 1"},
            ]
        }
        
        with patch("app.tools.search.tavily_client", mock_client):
            result = await tavily_search("test query")
        
        assert result["success"] is True
        assert result["source"] == "tavily"
    
    @pytest.mark.asyncio
    async def test_tavily_no_client(self):
        """無 Tavily client 時失敗"""
        from app.tools.search import tavily_search
        
        with patch("app.tools.search.tavily_client", None):
            result = await tavily_search("test query")
        
        assert result["success"] is False


# ============================================================
# DuckDuckGo Search Tests
# ============================================================

class TestDuckDuckGoSearch:
    """DuckDuckGo 搜尋測試"""
    
    @pytest.mark.asyncio
    async def test_duckduckgo_search_success(self):
        """DuckDuckGo 搜尋成功"""
        from app.tools.search import duckduckgo_search
        
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = [
            {"title": "Result 1", "body": "Content 1"},
        ]
        
        with patch("app.tools.search.DDGS", return_value=mock_ddgs_instance):
            result = await duckduckgo_search("test query")
        
        assert result["success"] is True
        assert result["source"] == "duckduckgo"
    
    @pytest.mark.asyncio
    async def test_duckduckgo_search_empty(self):
        """DuckDuckGo 無結果"""
        from app.tools.search import duckduckgo_search
        
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = []
        
        with patch("app.tools.search.DDGS", return_value=mock_ddgs_instance):
            result = await duckduckgo_search("test query")
        
        assert result["success"] is False


# ============================================================
# Graceful Degradation Tests
# ============================================================

class TestGracefulDegradation:
    """優雅降級測試"""
    
    @pytest.mark.asyncio
    async def test_all_search_fail_graceful_degradation(self):
        """所有搜尋都失敗時返回降級訊息"""
        from app.tools.search import web_search
        
        # Mock both search functions to fail
        with patch("app.tools.search.tavily_search", new_callable=AsyncMock) as mock_tavily:
            with patch("app.tools.search.duckduckgo_search", new_callable=AsyncMock) as mock_ddg:
                mock_tavily.return_value = {"success": False, "error": "Tavily error"}
                mock_ddg.return_value = {"success": False, "error": "DDG error"}
                
                result = await web_search("test query")
        
        # Should return fallback message
        assert result["success"] is False
        assert result["source"] == "fallback"
        assert "formatted" in result


# ============================================================
# Result Formatting Tests
# ============================================================

class TestResultFormatting:
    """搜尋結果格式化測試"""
    
    def test_format_tavily_results(self):
        """Tavily 結果格式化"""
        from app.tools.search import format_results
        
        results = [
            {"title": "Title 1", "content": "Content 1"},
            {"title": "Title 2", "content": "Content 2"},
        ]
        
        formatted = format_results(results, "tavily")
        
        assert "[TAVILY]" in formatted
        assert "Title 1" in formatted
    
    def test_format_ddg_results(self):
        """DuckDuckGo 結果格式化"""
        from app.tools.search import format_results
        
        results = [
            {"title": "Title 1", "body": "Body 1"},
            {"title": "Title 2", "body": "Body 2"},
        ]
        
        formatted = format_results(results, "duckduckgo")
        
        assert "[DUCKDUCKGO]" in formatted
        assert "Title 1" in formatted
