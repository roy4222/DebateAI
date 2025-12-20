export default function AboutPage() {
  return (
    <div className="flex-1 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-6">ℹ️ 關於我們</h1>
        <div className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-6 space-y-4">
          <p className="text-slate-300">
            <strong className="text-white">DebateAI</strong> 是一個 Multi-Agent
            即時辯論平台， 讓 AI 辯手針對各種議題進行深度辯論。
          </p>
          <p className="text-slate-400">此頁面正在開發中...</p>
        </div>
      </div>
    </div>
  );
}
