"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";

export default function AboutPage() {
  const { t, locale } = useI18n();

  return (
    <div className="flex-1 bg-gradient-to-br from-slate-100 via-slate-50 to-white dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="space-y-3">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white">
            DebateAI
          </h1>
          <p className="text-slate-600 dark:text-slate-300">
            {locale === "en"
              ? 'Focused on "features" and "experience": real-time streaming debates, multi-agent collaboration, intelligent search verification, and automatic summarization.'
              : "專注在「功能」與「體驗」：即時串流辯論、多 Agent 協作、智能搜尋查核與自動總結。"}
          </p>
        </header>

        <section className="space-y-8">
          {/* 核心優勢 */}
          <div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
              {locale === "en" ? "Why Choose DebateAI" : "為什麼選擇 DebateAI"}
            </h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-xl bg-purple-100 dark:bg-purple-500/10 border border-purple-300 dark:border-purple-500/30 p-4">
                <p className="text-slate-900 dark:text-white font-bold">
                  ⚙️ {locale === "en" ? "Smart Automation" : "聰明的自動化"}
                </p>
                <p className="text-slate-600 dark:text-slate-400 text-sm mt-2">
                  {locale === "en"
                    ? "Agent autonomously decides when to search and when to cite. Complete state tracking and error recovery."
                    : "Agent 自主判斷何時搜尋、何時引用，你不需手動干預。完整的狀態追蹤與錯誤恢復。"}
                </p>
              </div>
              <div className="rounded-xl bg-blue-100 dark:bg-blue-500/10 border border-blue-300 dark:border-blue-500/30 p-4">
                <p className="text-slate-900 dark:text-white font-bold">
                  ⚡{" "}
                  {locale === "en"
                    ? "High-Performance Real-time"
                    : "高性能實時體驗"}
                </p>
                <p className="text-slate-600 dark:text-slate-400 text-sm mt-2">
                  {locale === "en"
                    ? "Groq LPU high-speed inference, Token-level Streaming, zero-latency typewriter effect."
                    : "Groq LPU 高速推理、Token-level Streaming、零延遲的打字機效果。每場辯論都是實況直播。"}
                </p>
              </div>
              <div className="rounded-xl bg-green-100 dark:bg-green-500/10 border border-green-300 dark:border-green-500/30 p-4">
                <p className="text-slate-900 dark:text-white font-bold">
                  🛡️{" "}
                  {locale === "en"
                    ? "Three-layer Fault Tolerance"
                    : "三層容錯可靠性"}
                </p>
                <p className="text-slate-600 dark:text-slate-400 text-sm mt-2">
                  {locale === "en"
                    ? "Search failures don't interrupt. Auto-downgrade to backup. Agent continues on training knowledge when offline."
                    : "搜尋失敗不中斷，自動降級至備援方案。即使離線，Agent 仍可基於訓練知識持續辯論。"}
                </p>
              </div>
              <div className="rounded-xl bg-yellow-100 dark:bg-yellow-500/10 border border-yellow-300 dark:border-yellow-500/30 p-4">
                <p className="text-slate-900 dark:text-white font-bold">
                  💰 {locale === "en" ? "Zero-cost Architecture" : "零成本架構"}
                </p>
                <p className="text-slate-600 dark:text-slate-400 text-sm mt-2">
                  {locale === "en"
                    ? "Tavily 1000 free/month, DuckDuckGo completely free, Cloud Run pay-per-use."
                    : "Tavily 月 1000 次免費、DuckDuckGo 完全免費、Cloud Run 按需計費。整個系統成本極低。"}
                </p>
              </div>
              <div className="rounded-xl bg-indigo-100 dark:bg-indigo-500/10 border border-indigo-300 dark:border-indigo-500/30 p-4">
                <p className="text-slate-900 dark:text-white font-bold">
                  📊{" "}
                  {locale === "en"
                    ? "Reliable Argument Tracking"
                    : "可信的論據追蹤"}
                </p>
                <p className="text-slate-600 dark:text-slate-400 text-sm mt-2">
                  {locale === "en"
                    ? "Every argument has source, confidence score, and summary. Users can see at a glance what's fact vs inference."
                    : "每個論點都有來源、信心度與摘要。用戶能一眼看透哪些是事實、哪些是推論。"}
                </p>
              </div>
              <div className="rounded-xl bg-cyan-100 dark:bg-cyan-500/10 border border-cyan-300 dark:border-cyan-500/30 p-4">
                <p className="text-slate-900 dark:text-white font-bold">
                  🎯 {locale === "en" ? "Structured Output" : "結構化輸出"}
                </p>
                <p className="text-slate-600 dark:text-slate-400 text-sm mt-2">
                  {locale === "en"
                    ? "Auto-generate issue matrix, argument comparison, balanced conclusions. Export, share, cite with one click."
                    : "自動生成爭點矩陣、論據對比、平衡結論。導出、分享、引用都是一鍵操作。"}
                </p>
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-6">
              {locale === "en" ? "Feature Details" : "功能詳解"}
            </h2>

            {/* 功能 1: 即時串流辯論 */}
            <div className="mb-6 overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700/50 bg-white/60 dark:bg-gradient-to-br dark:from-slate-800/40 dark:to-slate-800/20 p-6">
              <div className="flex items-start gap-4">
                <div className="text-3xl flex-shrink-0">⚡</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                    {locale === "en"
                      ? "Real-time Streaming Debate"
                      : "即時串流辯論"}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                    {locale === "en"
                      ? "After entering a topic, AI debaters display responses character by character in real-time. Supports multi-round conversations and automatic speaker switching."
                      : "輸入主題後，AI 辯手逐字即時呈現回應，無需等待完整生成。每個字迅速鮮活地出現，打造沉浸式的辯論體驗。支援多輪對話與自動切換發言者，讓用戶如同觀看實況對話。"}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <span className="inline-block px-3 py-1 rounded-full text-xs bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-300 border border-purple-300 dark:border-purple-500/30">
                      Token Streaming
                    </span>
                    <span className="inline-block px-3 py-1 rounded-full text-xs bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-300 border border-purple-300 dark:border-purple-500/30">
                      {locale === "en" ? "Multi-round" : "多輪對話"}
                    </span>
                    <span className="inline-block px-3 py-1 rounded-full text-xs bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-300 border border-purple-300 dark:border-purple-500/30">
                      {locale === "en" ? "Auto-switch" : "自動輪換"}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* 功能 2: 多角色協作 */}
            <div className="mb-6 overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700/50 bg-white/60 dark:bg-gradient-to-br dark:from-slate-800/40 dark:to-slate-800/20 p-6">
              <div className="flex items-start gap-4">
                <div className="text-3xl flex-shrink-0">🤖</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">
                    {locale === "en"
                      ? "Multi-role Collaboration"
                      : "多角色協作與互動"}
                  </h3>
                  <div className="space-y-2">
                    <div className="rounded-lg bg-slate-100 dark:bg-slate-700/30 p-3">
                      <p className="text-slate-900 dark:text-white font-semibold">
                        Optimist（{locale === "en" ? "Optimist" : "樂觀者"}）
                      </p>
                      <p className="text-slate-600 dark:text-slate-400 text-sm">
                        {locale === "en"
                          ? "Emphasizes opportunities and advantages, interprets topics from a positive angle."
                          : "強調機會與優勢，從正面角度詮釋議題。基於 LangGraph 狀態管理自動維護論述上下文。"}
                      </p>
                    </div>
                    <div className="rounded-lg bg-slate-100 dark:bg-slate-700/30 p-3">
                      <p className="text-slate-900 dark:text-white font-semibold">
                        Skeptic（{locale === "en" ? "Skeptic" : "懷疑者"}）
                      </p>
                      <p className="text-slate-600 dark:text-slate-400 text-sm">
                        {locale === "en"
                          ? "Critiques risks and logical flaws, raises rebuttals and challenges with real-time fact verification."
                          : "批判風險與邏輯漏洞，提出反駁與挑戰。透過工具調用進行實時事實驗證。"}
                      </p>
                    </div>
                    <div className="rounded-lg bg-slate-100 dark:bg-slate-700/30 p-3">
                      <p className="text-slate-900 dark:text-white font-semibold">
                        Moderator（{locale === "en" ? "Moderator" : "主持人"}）
                      </p>
                      <p className="text-slate-600 dark:text-slate-400 text-sm">
                        {locale === "en"
                          ? "Triggered when debate reaches round limit, reads full history to produce balanced summary and conclusions."
                          : "在辯論達到上限輪數時觸發，閱讀完整歷史並產生平衡總結、關鍵洞察與結論。"}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 功能 3: 智能搜尋查核 */}
            <div className="mb-6 overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700/50 bg-white/60 dark:bg-gradient-to-br dark:from-slate-800/40 dark:to-slate-800/20 p-6">
              <div className="flex items-start gap-4">
                <div className="text-3xl flex-shrink-0">🔍</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                    {locale === "en"
                      ? "Intelligent Search & Three-layer Fallback"
                      : "智能搜尋與三層容錯"}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-3">
                    {locale === "en"
                      ? "Agent automatically decides when to fetch online data. Three-layer fallback mechanism:"
                      : "Agent 自動判斷何時需要聯網補充數據。若論點缺乏證據支撐，立即調用搜尋工具進行事實查核。採用三層容錯機制："}
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 dark:bg-green-500/20 text-green-600 dark:text-green-400 flex items-center justify-center font-bold">
                        1
                      </div>
                      <div>
                        <p className="text-slate-900 dark:text-white font-semibold">
                          Tavily API（{locale === "en" ? "Primary" : "主要"}）
                        </p>
                        <p className="text-slate-600 dark:text-slate-400 text-sm">
                          {locale === "en"
                            ? "AI-optimized search, 1000 free/month"
                            : "專為 AI 設計的搜尋引擎，月 1000 次免費"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-yellow-100 dark:bg-yellow-500/20 text-yellow-600 dark:text-yellow-400 flex items-center justify-center font-bold">
                        2
                      </div>
                      <div>
                        <p className="text-slate-900 dark:text-white font-semibold">
                          DuckDuckGo Text（{locale === "en" ? "Backup" : "備援"}
                          ）
                        </p>
                        <p className="text-slate-600 dark:text-slate-400 text-sm">
                          {locale === "en"
                            ? "Completely free, auto-fallback when Tavily fails"
                            : "完全免費，文字摘要搜尋，當 Tavily 失敗時自動降級"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold">
                        3
                      </div>
                      <div>
                        <p className="text-slate-900 dark:text-white font-semibold">
                          {locale === "en"
                            ? "Graceful Degradation"
                            : "優雅降級"}
                        </p>
                        <p className="text-slate-600 dark:text-slate-400 text-sm">
                          {locale === "en"
                            ? "When search fully fails, Agent continues on training knowledge"
                            : "搜尋完全失敗時，Agent 基於訓練知識繼續辯論，無中斷"}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <footer className="text-slate-500 text-sm">
          {locale === "en"
            ? "Last updated: 2025-12-26 • Version v0.4.0"
            : "最後更新：2025-12-26 ・ 版本 v0.4.0"}
        </footer>
      </div>
    </div>
  );
}
