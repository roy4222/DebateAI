"""
DebateAI - 網路搜尋工具模組

三層容錯策略：
1. Tavily（主）- 專為 AI 設計，極度穩定
2. DuckDuckGo（備援）- 免費無限次數
3. 優雅降級 - 搜尋失敗不影響辯論
"""

from tavily import TavilyClient
from duckduckgo_search import DDGS
import os
import asyncio

# 初始化 Tavily 客戶端（可選）
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY")) if os.getenv("TAVILY_API_KEY") else None


async def tavily_search(query: str) -> dict:
    """第一層：Tavily 搜尋（專業 AI 搜尋）"""
    if not tavily_client:
        return {"success": False, "error": "No Tavily API key"}

    try:
        # Tavily 是同步的，用 asyncio 包裝
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: tavily_client.search(query, max_results=3, search_depth="basic")
        )

        results = response.get("results", [])
        if not results:
            return {"success": False, "error": "No results"}

        return {
            "success": True,
            "results": results,
            "source": "tavily"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def duckduckgo_search(query: str) -> dict:
    """第二層：DuckDuckGo 搜尋（免費備援）"""
    try:
        # DDGS 是同步的，用 asyncio 包裝
        loop = asyncio.get_event_loop()
        ddgs = DDGS()
        results = await loop.run_in_executor(
            None,
            lambda: list(ddgs.text(query, max_results=3))
        )

        if not results:
            return {"success": False, "error": "No results"}

        return {
            "success": True,
            "results": results,
            "source": "duckduckgo"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def web_search(query: str) -> dict:
    """三層容錯網路搜尋

    Args:
        query: 搜尋關鍵字

    Returns:
        dict: {
            "success": bool,
            "results": list,  # 搜尋結果（如果成功）
            "source": str,    # "tavily" | "duckduckgo" | "fallback"
            "formatted": str  # 格式化的結果文字
        }
    """

    # 第一層：Tavily
    result = await tavily_search(query)
    if result["success"]:
        formatted = format_results(result["results"], result["source"])
        return {**result, "formatted": formatted}

    # 第二層：DuckDuckGo
    result = await duckduckgo_search(query)
    if result["success"]:
        formatted = format_results(result["results"], result["source"])
        return {**result, "formatted": formatted}

    # 第三層：優雅降級
    return {
        "success": False,
        "source": "fallback",
        "formatted": f"[注意] 搜尋功能暫時無法使用，Agent 將基於現有知識回答關於「{query}」的問題。"
    }


def format_results(results: list, source: str) -> str:
    """格式化搜尋結果為可讀文字

    Args:
        results: 搜尋結果列表
        source: 來源（"tavily" | "duckduckgo"）

    Returns:
        格式化的文字
    """
    # 根據來源選擇內容欄位（Tavily 用 content，DuckDuckGo 用 body）
    content_key = "content" if source == "tavily" else "body"
    lines = [
        f"• {r.get('title', '未知標題')}: {r.get(content_key, '')[:200]}..."
        for r in results[:3]
    ]
    
    formatted = "\n".join(lines)
    return f"[{source.upper()}] 搜尋結果：\n{formatted}"

