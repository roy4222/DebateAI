"use client";

import { useState, useEffect } from "react";
import axios from "axios";

// API 基礎 URL
const API_URL = "http://127.0.0.1:8001";

// Job 類型定義
interface Job {
  postid: number;
  company: string;
  content: string;
  pdate: string;
}

// 新增/修改 Job 的表單
interface JobForm {
  company: string;
  content: string;
}

export default function Home() {
  // 狀態管理
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 表單狀態
  const [formData, setFormData] = useState<JobForm>({
    company: "",
    content: "",
  });
  const [editingId, setEditingId] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);

  // ========== 讀取所有職缺 (GET) ==========
  async function fetchJobs() {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${API_URL}/job/`);
      setJobs(response.data);
    } catch (err) {
      setError("無法載入資料，請確認 API 是否運行中");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  // 頁面載入時取得資料
  useEffect(() => {
    fetchJobs();
  }, []);

  // ========== 新增職缺 (POST) ==========
  async function createJob() {
    if (!formData.company || !formData.content) {
      setError("請填寫所有欄位");
      return;
    }
    try {
      await axios.post(`${API_URL}/job/`, formData);
      setFormData({ company: "", content: "" });
      setShowForm(false);
      fetchJobs(); // 重新載入資料
    } catch (err) {
      setError("新增失敗");
      console.error(err);
    }
  }

  // ========== 修改職缺 (PUT) ==========
  async function updateJob() {
    if (!editingId) return;
    try {
      await axios.put(`${API_URL}/job/${editingId}`, formData);
      setFormData({ company: "", content: "" });
      setEditingId(null);
      setShowForm(false);
      fetchJobs(); // 重新載入資料
    } catch (err) {
      setError("修改失敗");
      console.error(err);
    }
  }

  // ========== 刪除職缺 (DELETE) ==========
  async function deleteJob(postid: number) {
    if (!confirm("確定要刪除這筆職缺嗎？")) return;
    try {
      await axios.delete(`${API_URL}/job/${postid}`);
      fetchJobs(); // 重新載入資料
    } catch (err) {
      setError("刪除失敗");
      console.error(err);
    }
  }

  // 開啟新增表單
  function openAddForm() {
    setFormData({ company: "", content: "" });
    setEditingId(null);
    setShowForm(true);
  }

  // 開啟編輯表單
  function openEditForm(job: Job) {
    setFormData({ company: job.company, content: job.content });
    setEditingId(job.postid);
    setShowForm(true);
  }

  // 處理表單提交
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (editingId) {
      updateJob();
    } else {
      createJob();
    }
  }

  return (
    <main className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* 標題 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🏢 職缺管理系統
          </h1>
          <p className="text-gray-600">
            進階Web程式設計 - 自主學習作業 (FastAPI + Next.js + Axios)
          </p>
        </div>

        {/* 錯誤訊息 */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
            <button
              onClick={() => setError("")}
              className="float-right font-bold"
            >
              ×
            </button>
          </div>
        )}

        {/* 操作按鈕 */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={openAddForm}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg font-medium transition"
          >
            ➕ 新增職缺
          </button>
          <button
            onClick={fetchJobs}
            className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 rounded-lg font-medium transition"
          >
            🔄 重新載入
          </button>
        </div>

        {/* 新增/修改表單 */}
        {showForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">
              {editingId ? "✏️ 修改職缺" : "➕ 新增職缺"}
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-gray-700 font-medium mb-2">
                  公司名稱
                </label>
                <input
                  type="text"
                  value={formData.company}
                  onChange={(e) =>
                    setFormData({ ...formData, company: e.target.value })
                  }
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="請輸入公司名稱"
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 font-medium mb-2">
                  職缺內容
                </label>
                <textarea
                  value={formData.content}
                  onChange={(e) =>
                    setFormData({ ...formData, content: e.target.value })
                  }
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="請輸入職缺內容"
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="submit"
                  className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg font-medium transition"
                >
                  {editingId ? "💾 儲存修改" : "✅ 確認新增"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="bg-gray-400 hover:bg-gray-500 text-white px-6 py-2 rounded-lg font-medium transition"
                >
                  取消
                </button>
              </div>
            </form>
          </div>
        )}

        {/* 職缺列表 */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="bg-gray-800 text-white px-6 py-4">
            <h2 className="text-xl font-bold">📋 職缺列表</h2>
          </div>

          {loading ? (
            <div className="p-8 text-center text-gray-500">載入中...</div>
          ) : jobs.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              目前沒有職缺資料
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-6 py-3 text-left text-gray-600">ID</th>
                  <th className="px-6 py-3 text-left text-gray-600">公司</th>
                  <th className="px-6 py-3 text-left text-gray-600">內容</th>
                  <th className="px-6 py-3 text-left text-gray-600">日期</th>
                  <th className="px-6 py-3 text-center text-gray-600">操作</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job) => (
                  <tr key={job.postid} className="border-t hover:bg-gray-50">
                    <td className="px-6 py-4 font-mono text-gray-500">
                      {job.postid}
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-800">
                      {job.company}
                    </td>
                    <td className="px-6 py-4 text-gray-600">{job.content}</td>
                    <td className="px-6 py-4 text-gray-500">{job.pdate}</td>
                    <td className="px-6 py-4 text-center">
                      <button
                        onClick={() => openEditForm(job)}
                        className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded mr-2 text-sm"
                      >
                        ✏️ 修改
                      </button>
                      <button
                        onClick={() => deleteJob(job.postid)}
                        className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm"
                      >
                        🗑️ 刪除
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* 技術說明 */}
        <div className="mt-6 bg-blue-50 rounded-lg p-6">
          <h3 className="font-bold text-blue-800 mb-2">🔧 技術說明</h3>
          <ul className="text-blue-700 text-sm space-y-1">
            <li>
              • <strong>Frontend:</strong> Next.js + TypeScript + Tailwind CSS
            </li>
            <li>
              • <strong>API 呼叫:</strong> Axios (GET, POST, PUT, DELETE)
            </li>
            <li>
              • <strong>Backend:</strong> FastAPI (Python)
            </li>
            <li>
              • <strong>資料庫:</strong> MySQL / 記憶體版本
            </li>
          </ul>
        </div>
      </div>
    </main>
  );
}
