import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function AboutPage() {
  return (
    <div className="flex-1 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="space-y-3">
          <h1 className="text-4xl font-bold text-white">DebateAI</h1>
          <p className="text-slate-300">
            專注在「功能」與「體驗」：即時串流辯論、多 Agent 協作、智能搜尋查核與自動總結。
          </p>
        </header>

        <section className="space-y-8">
          {/* 核心優勢 */}
          <div>
            <h2 className="text-2xl font-bold text-white mb-4">為什麼選擇 DebateAI</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-xl bg-purple-500/10 border border-purple-500/30 p-4">
                <p className="text-white font-bold">⚙️ 聰明的自動化</p>
                <p className="text-slate-400 text-sm mt-2">Agent 自主判斷何時搜尋、何時引用，你不需手動干預。完整的狀態追蹤與錯誤恢復。</p>
              </div>
              <div className="rounded-xl bg-blue-500/10 border border-blue-500/30 p-4">
                <p className="text-white font-bold">⚡ 高性能實時體驗</p>
                <p className="text-slate-400 text-sm mt-2">Groq LPU 高速推理、Token-level Streaming、零延遲的打字機效果。每場辯論都是實況直播。</p>
              </div>
              <div className="rounded-xl bg-green-500/10 border border-green-500/30 p-4">
                <p className="text-white font-bold">🛡️ 三層容錯可靠性</p>
                <p className="text-slate-400 text-sm mt-2">搜尋失敗不中斷，自動降級至備援方案。即使離線，Agent 仍可基於訓練知識持續辯論。</p>
              </div>
              <div className="rounded-xl bg-yellow-500/10 border border-yellow-500/30 p-4">
                <p className="text-white font-bold">💰 零成本架構</p>
                <p className="text-slate-400 text-sm mt-2">Tavily 月 1000 次免費、DuckDuckGo 完全免費、Cloud Run 按需計費。整個系統成本極低。</p>
              </div>
              <div className="rounded-xl bg-indigo-500/10 border border-indigo-500/30 p-4">
                <p className="text-white font-bold">📊 可信的論據追蹤</p>
                <p className="text-slate-400 text-sm mt-2">每個論點都有來源、信心度與摘要。用戶能一眼看透哪些是事實、哪些是推論。</p>
              </div>
              <div className="rounded-xl bg-cyan-500/10 border border-cyan-500/30 p-4">
                <p className="text-white font-bold">🎯 結構化輸出</p>
                <p className="text-slate-400 text-sm mt-2">自動生成爭點矩陣、論據對比、平衡結論。導出、分享、引用都是一鍵操作。</p>
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-3xl font-bold text-white mb-6">功能詳解</h2>
            
            {/* 功能 1: 即時串流辯論 */}
            <div className="mb-6 overflow-hidden rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-800/40 to-slate-800/20 p-6">
              <div className="flex items-start gap-4">
                <div className="text-3xl flex-shrink-0">⚡</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">即時串流辯論</h3>
                  <p className="text-slate-300 leading-relaxed">
                    輸入主題後，AI 辯手逐字即時呈現回應，無需等待完整生成。每個字迅速鮮活地出現，打造沉浸式的辯論體驗。支援多輪對話與自動切換發言者，讓用戶如同觀看實況對話。
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <span className="inline-block px-3 py-1 rounded-full text-xs bg-purple-500/20 text-purple-300 border border-purple-500/30">Token Streaming</span>
                    <span className="inline-block px-3 py-1 rounded-full text-xs bg-purple-500/20 text-purple-300 border border-purple-500/30">多輪對話</span>
                    <span className="inline-block px-3 py-1 rounded-full text-xs bg-purple-500/20 text-purple-300 border border-purple-500/30">自動輪換</span>
                  </div>
                </div>
              </div>
            </div>

            {/* 功能 2: 多角色協作 */}
            <div className="mb-6 overflow-hidden rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-800/40 to-slate-800/20 p-6">
              <div className="flex items-start gap-4">
                <div className="text-3xl flex-shrink-0">🤖</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-3">多角色協作與互動</h3>
                  <div className="space-y-2">
                    <div className="rounded-lg bg-slate-700/30 p-3">
                      <p className="text-white font-semibold">Optimist（樂觀者）</p>
                      <p className="text-slate-400 text-sm">強調機會與優勢，從正面角度詮釋議題。基於 LangGraph 狀態管理自動維護論述上下文。</p>
                    </div>
                    <div className="rounded-lg bg-slate-700/30 p-3">
                      <p className="text-white font-semibold">Skeptic（懷疑者）</p>
                      <p className="text-slate-400 text-sm">批判風險與邏輯漏洞，提出反駁與挑戰。透過工具調用進行實時事實驗證。</p>
                    </div>
                    <div className="rounded-lg bg-slate-700/30 p-3">
                      <p className="text-white font-semibold">Moderator（主持人）</p>
                      <p className="text-slate-400 text-sm">在辯論達到上限輪數時觸發，閱讀完整歷史並產生平衡總結、關鍵洞察與結論。</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 功能 3: 智能搜尋查核 */}
            <div className="mb-6 overflow-hidden rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-800/40 to-slate-800/20 p-6">
              <div className="flex items-start gap-4">
                <div className="text-3xl flex-shrink-0">🔍</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">智能搜尋與三層容錯</h3>
                  <p className="text-slate-300 leading-relaxed mb-3">
                    Agent 自動判斷何時需要聯網補充數據。若論點缺乏證據支撐，立即調用搜尋工具進行事實查核。採用三層容錯機制：
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center font-bold">1</div>
                      <div>
                        <p className="text-white font-semibold">Tavily API（主要）</p>
                        <p className="text-slate-400 text-sm">專為 AI 設計的搜尋引擎，已清洗內容、高相關度、<span className="text-slate-300">月 1000 次免費</span></p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-yellow-500/20 text-yellow-400 flex items-center justify-center font-bold">2</div>
                      <div>
                        <p className="text-white font-semibold">DuckDuckGo Text（備援）</p>
                        <p className="text-slate-400 text-sm">完全免費，文字摘要搜尋，當 Tavily 失敗時自動降級</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold">3</div>
                      <div>
                        <p className="text-white font-semibold">優雅降級</p>
                        <p className="text-slate-400 text-sm">搜尋完全失敗時，Agent 基於訓練知識繼續辯論，無中斷</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 功能 4: 事實卡與來源 */}
            <div className="mb-6 overflow-hidden rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-800/40 to-slate-800/20 p-6">
              <div className="flex items-start gap-4">
                <div className="text-3xl flex-shrink-0">📋</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">事實卡與來源追蹤</h3>
                  <p className="text-slate-300 leading-relaxed">
                    搜尋結果即時視覺化成「事實卡」，每張卡片包含：引用來源網址、信心度評分、內容摘要與引用標記。側邊欄實時追蹤每個論據的驗證狀態，建立完整可信的論述鏈。用戶可一鍵檢視來源、展開全文或分享引用。<span className="text-slate-400 text-sm">（Phase 3+ 功能）</span>
                  </p>
                </div>
              </div>
            </div>

            {/* 功能 5: 狀態與反饋 */}
            <div className="mb-6 overflow-hidden rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-800/40 to-slate-800/20 p-6">
              <div className="flex items-start gap-4">
                <div className="text-3xl flex-shrink-0">💭</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">實時狀態反饋</h3>
                  <p className="text-slate-300 leading-relaxed mb-3">
                    前端即時顯示 Agent 的處理狀態，使用清晰的動態提示減少用戶等待焦慮：
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    <div className="rounded-lg bg-slate-700/30 px-3 py-2 text-slate-300 text-sm">
                      <span className="inline-block w-2 h-2 rounded-full bg-purple-400 mr-2 animate-pulse"></span>
                      正在思考中…
                    </div>
                    <div className="rounded-lg bg-slate-700/30 px-3 py-2 text-slate-300 text-sm">
                      <span className="inline-block w-2 h-2 rounded-full bg-blue-400 mr-2 animate-pulse"></span>
                      搜尋中…
                    </div>
                    <div className="rounded-lg bg-slate-700/30 px-3 py-2 text-slate-300 text-sm">
                      <span className="inline-block w-2 h-2 rounded-full bg-green-400 mr-2 animate-pulse"></span>
                      結果載入中…
                    </div>
                    <div className="rounded-lg bg-slate-700/30 px-3 py-2 text-slate-300 text-sm">
                      <span className="inline-block w-2 h-2 rounded-full bg-yellow-400 mr-2 animate-pulse"></span>
                      正在回應…
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 功能 6: 自動總結報告 */}
            <div className="mb-6 overflow-hidden rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-800/40 to-slate-800/20 p-6">
              <div className="flex items-start gap-4">
                <div className="text-3xl flex-shrink-0">📊</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">自動總結與結論</h3>
                  <p className="text-slate-300 leading-relaxed mb-3">
                    辯論結束或達到回合上限後，Moderator Agent 自動分析整場對話並生成結構化報告：
                  </p>
                  <ul className="space-y-2 text-slate-300">
                    <li className="flex gap-2">
                      <span className="text-purple-400 font-bold">✓</span>
                      <span><strong>爭點列表</strong>：討論的核心議題與子議題</span>
                    </li>
                    <li className="flex gap-2">
                      <span className="text-purple-400 font-bold">✓</span>
                      <span><strong>雙方論據</strong>：Optimist 與 Skeptic 各自的核心論點與證據</span>
                    </li>
                    <li className="flex gap-2">
                      <span className="text-purple-400 font-bold">✓</span>
                      <span><strong>平衡結論</strong>：中立視角綜合雙方立場的最終洞察</span>
                    </li>
                    <li className="flex gap-2">
                      <span className="text-purple-400 font-bold">✓</span>
                      <span><strong>建議與展望</strong>：針對議題的進一步思考方向</span>
                    </li>
                  </ul>
                  <p className="text-slate-400 text-sm mt-3">用戶可一鍵導出或分享整場辯論摘要，支援多種格式。</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <footer className="text-slate-500 text-sm">
          最後更新：2025-12-10 ・ 版本 v0.2.0
        </footer>
      </div>
    </div>
  );
}
