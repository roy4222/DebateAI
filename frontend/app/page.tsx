'use client';
import { useState, useEffect } from 'react';

export default function Home() {
  const [status, setStatus] = useState('Connecting to backend...');

  useEffect(() => {
    // 嘗試連線到 FastAPI
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => setStatus(data.message))
      .catch(() => setStatus('Connection Failed ❌ (Check backend console)'));
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white font-sans">
      <h1 className="text-5xl font-extrabold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
        DebateAI 🤖
      </h1>
      <div className="p-6 border border-gray-700 rounded-xl bg-gray-800 shadow-2xl">
        <p className="text-gray-400 text-sm mb-2 uppercase tracking-wider">System Status</p>
        <p className="text-xl font-mono text-green-400 flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></span>
          {status}
        </p>
      </div>
    </div>
  );
}