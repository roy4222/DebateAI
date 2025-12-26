"""
DebateAI Backend Test Fixtures

提供 Mock fixtures 用於測試：
- Supabase client
- Groq LLM（含 Rate Limit 模擬）
- Search tools（Tavily/DuckDuckGo）
- FastAPI AsyncClient
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone

# ============================================================
# Sample Test Data
# ============================================================

SAMPLE_MESSAGES = [
    {
        "version": 1,
        "type": "ai",
        "node": "optimist",
        "content": "這是樂觀者的觀點...",
        "roundInfo": "第 1 輪",
        "timestamp": "2025-12-26T10:00:00Z"
    },
    {
        "version": 1,
        "type": "ai",
        "node": "skeptic",
        "content": "這是懷疑者的反駁...",
        "roundInfo": "第 1 輪",
        "timestamp": "2025-12-26T10:00:30Z"
    },
    {
        "version": 1,
        "type": "ai",
        "node": "moderator",
        "content": "### 🔄 第 1 輪小結\n...",
        "roundInfo": None,
        "timestamp": "2025-12-26T10:01:00Z"
    }
]

SAMPLE_DEBATE_SUMMARY = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "topic": "測試主題",
    "created_at": "2025-12-26T10:00:00Z",
    "rounds_completed": 3
}

SAMPLE_DEBATE_DETAIL = {
    **SAMPLE_DEBATE_SUMMARY,
    "messages": SAMPLE_MESSAGES,
    "max_rounds": 3,
    "updated_at": "2025-12-26T10:05:00Z"
}

SAMPLE_FRONTEND_MESSAGES = [
    {"node": "optimist", "text": "這是樂觀者的觀點...", "roundInfo": "第 1 輪"},
    {"node": "skeptic", "text": "這是懷疑者的反駁...", "roundInfo": "第 1 輪"},
]


# ============================================================
# Supabase Fixtures
# ============================================================

@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    mock_client = MagicMock()
    
    # Mock table().insert().execute() chain
    mock_insert_result = MagicMock()
    mock_insert_result.data = [{"id": "550e8400-e29b-41d4-a716-446655440000"}]
    
    mock_table = MagicMock()
    mock_table.insert.return_value.execute.return_value = mock_insert_result
    mock_table.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[SAMPLE_DEBATE_SUMMARY]
    )
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
        data=SAMPLE_DEBATE_DETAIL
    )
    
    mock_client.table.return_value = mock_table
    
    with patch("app.supabase_client.get_supabase", return_value=mock_client):
        with patch("app.supabase_client.is_supabase_enabled", return_value=True):
            yield mock_client


@pytest.fixture
def mock_supabase_disabled():
    """Mock Supabase disabled"""
    with patch("app.supabase_client.is_supabase_enabled", return_value=False):
        yield


# ============================================================
# LLM Fixtures
# ============================================================

@pytest.fixture
def mock_groq_llm():
    """Mock ChatGroq LLM"""
    mock_response = MagicMock()
    mock_response.content = "這是 AI 的測試回應。"
    mock_response.tool_calls = None
    
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)
    
    with patch("app.graph.ChatGroq", return_value=mock_llm):
        yield mock_llm


@pytest.fixture
def mock_groq_llm_rate_limit():
    """Mock ChatGroq with 429 rate limit error"""
    from groq import RateLimitError
    
    # First call raises 429, second call succeeds
    call_count = 0
    
    async def mock_ainvoke(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("429 Too Many Requests")
        mock_response = MagicMock()
        mock_response.content = "使用備用模型的回應"
        mock_response.tool_calls = None
        return mock_response
    
    mock_llm = MagicMock()
    mock_llm.ainvoke = mock_ainvoke
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)
    
    with patch("app.graph.ChatGroq", return_value=mock_llm):
        yield mock_llm


# ============================================================
# Search Tool Fixtures
# ============================================================

@pytest.fixture
def mock_search_tavily():
    """Mock Tavily search success"""
    mock_result = {
        "source": "tavily",
        "formatted": "[TAVILY] 搜尋結果：\n• 結果 1\n• 結果 2",
        "raw": [{"title": "結果 1", "content": "內容 1"}]
    }
    
    with patch("app.tools.search.web_search", new_callable=AsyncMock) as mock:
        mock.return_value = mock_result
        yield mock


@pytest.fixture
def mock_search_failure():
    """Mock search failure with graceful degradation"""
    mock_result = {
        "source": "fallback",
        "formatted": "⚠️ 搜尋功能暫時無法使用",
        "raw": []
    }
    
    with patch("app.tools.search.web_search", new_callable=AsyncMock) as mock:
        mock.return_value = mock_result
        yield mock


# ============================================================
# FastAPI Client Fixture
# ============================================================

@pytest.fixture
async def async_client():
    """FastAPI async test client"""
    from app.main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ============================================================
# Environment Variable Fixtures
# ============================================================

@pytest.fixture
def env_fake_stream(monkeypatch):
    """Set USE_FAKE_STREAM=true"""
    monkeypatch.setenv("USE_FAKE_STREAM", "true")
    yield


@pytest.fixture
def env_langgraph(monkeypatch):
    """Set USE_LANGGRAPH=true"""
    monkeypatch.setenv("USE_LANGGRAPH", "true")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    yield
