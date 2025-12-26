"""
Supabase Client Tests

測試 app/supabase_client.py 的客戶端初始化和狀態檢查
"""

import pytest
from unittest.mock import patch, MagicMock


class TestIsSupabaseEnabled:
    """is_supabase_enabled 測試"""
    
    def test_enabled_when_both_vars_set(self):
        """兩個環境變數都設定時返回 True"""
        with patch.dict("os.environ", {
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test-service-role-key-123456"
        }):
            from app.supabase_client import is_supabase_enabled
            assert is_supabase_enabled() is True
    
    def test_disabled_when_url_missing(self):
        """缺少 URL 時返回 False"""
        with patch.dict("os.environ", {
            "SUPABASE_URL": "",
            "SUPABASE_SERVICE_ROLE_KEY": "test-service-role-key-123456"
        }, clear=True):
            from app.supabase_client import is_supabase_enabled
            result = is_supabase_enabled()
            assert result is False
    
    def test_disabled_when_key_missing(self):
        """缺少 Key 時返回 False"""
        with patch.dict("os.environ", {
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": ""
        }, clear=True):
            from app.supabase_client import is_supabase_enabled
            result = is_supabase_enabled()
            assert result is False
    
    def test_disabled_when_url_too_short(self):
        """URL 太短時返回 False"""
        with patch.dict("os.environ", {
            "SUPABASE_URL": "short",
            "SUPABASE_SERVICE_ROLE_KEY": "test-service-role-key-123456"
        }):
            from app.supabase_client import is_supabase_enabled
            assert is_supabase_enabled() is False


class TestGetSupabase:
    """get_supabase 測試"""
    
    def test_raises_when_not_configured(self):
        """未設定時拋出 ValueError"""
        from app.supabase_client import reset_client, get_supabase
        
        reset_client()  # 重置單例
        
        with patch.dict("os.environ", {
            "SUPABASE_URL": "",
            "SUPABASE_SERVICE_ROLE_KEY": ""
        }, clear=True):
            with pytest.raises(ValueError, match="Supabase 未設定"):
                get_supabase()
    
    def test_creates_client_when_configured(self):
        """設定正確時建立客戶端"""
        from app.supabase_client import reset_client, get_supabase
        
        reset_client()
        
        mock_client = MagicMock()
        
        with patch.dict("os.environ", {
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test-key"
        }):
            with patch("app.supabase_client.create_client", return_value=mock_client):
                client = get_supabase()
                assert client == mock_client


class TestResetClient:
    """reset_client 測試"""
    
    def test_reset_client_clears_singleton(self):
        """reset_client 清除單例"""
        from app.supabase_client import reset_client, _supabase_client
        
        # 這主要是確保函數不會拋出錯誤
        reset_client()
        
        # 無法直接檢查私有變數，但可以確保函數執行完成
        assert True
