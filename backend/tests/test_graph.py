"""
LangGraph State Management Tests

測試 app/graph.py 的狀態管理和 Rate Limit 容錯
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os


# ============================================================
# State Initialization Tests
# ============================================================

class TestCreateInitialState:
    """create_initial_state 測試"""
    
    def test_create_initial_state_defaults(self):
        """預設狀態初始化"""
        from app.graph import create_initial_state
        
        state = create_initial_state("測試主題")
        
        assert state["topic"] == "測試主題"
        assert state["current_speaker"] == "optimist"
        assert state["round_count"] == 0
        assert state["max_rounds"] == 3
        assert state["tool_iterations"] == 0
        assert state["last_agent"] == ""
        assert state["messages"] == []
    
    def test_create_initial_state_custom_rounds(self):
        """自訂輪數"""
        from app.graph import create_initial_state
        
        state = create_initial_state("測試主題", max_rounds=5)
        
        assert state["max_rounds"] == 5


# ============================================================
# Prompt Building Tests
# ============================================================

class TestBuildPrompt:
    """build_prompt 測試"""
    
    def test_build_optimist_prompt_opening(self):
        """樂觀者開場白 prompt"""
        from app.graph import create_initial_state, build_prompt
        
        state = create_initial_state("AI 的未來")
        messages = build_prompt(state, "optimist")
        
        assert len(messages) == 2  # System + User
        assert "樂觀辯手" in messages[0].content
        assert "開場白" in messages[1].content
    
    def test_build_skeptic_prompt(self):
        """懷疑者 prompt"""
        from app.graph import create_initial_state, build_prompt
        from langchain_core.messages import AIMessage
        
        state = create_initial_state("AI 的未來")
        state["messages"] = [AIMessage(content="樂觀觀點", name="optimist")]
        
        messages = build_prompt(state, "skeptic")
        
        assert "懷疑辯手" in messages[0].content
        assert "反駁" in messages[1].content


# ============================================================
# Format Messages Tests
# ============================================================

class TestFormatMessages:
    """format_messages 測試"""
    
    def test_format_empty_messages(self):
        """空訊息列表"""
        from app.graph import format_messages
        
        result = format_messages([])
        
        assert result == "(尚無對話)"
    
    def test_format_with_limit(self):
        """限制訊息數量"""
        from app.graph import format_messages
        from langchain_core.messages import AIMessage
        
        messages = [AIMessage(content=f"訊息 {i}", name="test") for i in range(10)]
        result = format_messages(messages, limit=4)
        
        # Should only contain last 4 messages
        assert "訊息 6" in result
        assert "訊息 9" in result


# ============================================================
# Rate Limit Retry LLM Tests
# ============================================================

class TestRateLimitRetryLLM:
    """RateLimitRetryLLM 模型切換測試"""
    
    def test_rate_limit_retry_llm_init(self):
        """初始化"""
        from app.graph import RateLimitRetryLLM
        
        llm = RateLimitRetryLLM(
            primary_model="model-a",
            fallback_models=["model-b", "model-c"],
            bind_tools=False
        )
        
        assert llm.primary_model == "model-a"
        assert llm.fallback_models == ["model-b", "model-c"]
    
    def test_get_available_model_no_cooldown(self):
        """無 cooldown 時返回主模型"""
        from app.graph import RateLimitRetryLLM
        
        # Clear class-level cooldown
        RateLimitRetryLLM.cooldown_models.clear()
        
        llm = RateLimitRetryLLM(
            primary_model="model-a",
            fallback_models=["model-b"],
            bind_tools=False
        )
        
        result = llm._get_available_model()
        assert result == "model-a"
    
    def test_get_available_model_with_cooldown(self):
        """主模型 cooldown 時返回備用模型"""
        from app.graph import RateLimitRetryLLM
        
        RateLimitRetryLLM.cooldown_models = {"model-a"}
        
        llm = RateLimitRetryLLM(
            primary_model="model-a",
            fallback_models=["model-b", "model-c"],
            bind_tools=False
        )
        
        result = llm._get_available_model()
        assert result == "model-b"
        
        # Cleanup
        RateLimitRetryLLM.cooldown_models.clear()
    
    def test_get_available_model_all_cooldown(self):
        """所有模型都 cooldown 時重置"""
        from app.graph import RateLimitRetryLLM
        
        RateLimitRetryLLM.cooldown_models = {"model-a", "model-b"}
        
        llm = RateLimitRetryLLM(
            primary_model="model-a",
            fallback_models=["model-b"],
            bind_tools=False
        )
        
        result = llm._get_available_model()
        
        # Should reset and return primary
        assert result == "model-a"
        assert len(RateLimitRetryLLM.cooldown_models) == 0


# ============================================================
# get_llm Factory Tests
# ============================================================

class TestGetLLM:
    """get_llm 工廠函數測試"""
    
    def test_get_llm_default_model(self, monkeypatch):
        """使用預設模型"""
        from app.graph import get_llm, RateLimitRetryLLM
        
        monkeypatch.delenv("GROQ_MODEL", raising=False)
        monkeypatch.setenv("GROQ_API_KEY", "test-key")
        
        llm = get_llm()
        
        assert isinstance(llm, RateLimitRetryLLM)
        assert llm.primary_model == "llama-3.1-8b-instant"
    
    def test_get_llm_custom_model(self, monkeypatch):
        """使用自訂模型"""
        from app.graph import get_llm, RateLimitRetryLLM
        
        monkeypatch.setenv("GROQ_MODEL", "custom-model")
        monkeypatch.setenv("GROQ_API_KEY", "test-key")
        
        llm = get_llm()
        
        assert llm.primary_model == "custom-model"
    
    def test_get_llm_with_tools(self, monkeypatch):
        """綁定工具"""
        from app.graph import get_llm, RateLimitRetryLLM
        
        monkeypatch.setenv("GROQ_API_KEY", "test-key")
        
        llm = get_llm(bind_tools=True)
        
        assert llm.bind_tools is True


# ============================================================
# Tool Iteration Limit Tests
# ============================================================

class TestToolIterationLimit:
    """工具迭代限制測試"""
    
    def test_max_tool_iterations(self):
        """最大迭代次數為 3"""
        from app.graph import MAX_TOOL_ITERATIONS
        
        assert MAX_TOOL_ITERATIONS == 3
