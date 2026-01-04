"""
FastAPI Demo - 自主學習作業

這個專案展示：
1. FastAPI 基礎 - 路由、參數處理、Pydantic 驗證
2. MySQL 整合 - 資料庫連線與 CRUD 操作
3. CORS 設定 - 允許前端 Axios 呼叫

啟動方式：
    fastapi dev main.py

測試 API：
    http://localhost:8000/docs (Swagger UI)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import job

# 建立 FastAPI 應用程式
app = FastAPI(
    title="Job API - 徵才系統",
    description="進階Web程式設計 - 自主學習作業 Demo",
    version="1.0.0"
)

# ========== CORS 設定 ==========
# 允許前端 (Next.js) 呼叫 API
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],          # 允許所有 HTTP 方法
    allow_headers=["*"],          # 允許所有 Headers
)

# ========== 引入 Router ==========
app.include_router(job.router)


# ========== 根路由 ==========
@app.get("/", tags=["Root"])
def root():
    """API 根路由 - Hello World"""
    return {"message": "Hello FastAPI! 歡迎使用職缺管理 API"}


@app.get("/health", tags=["Root"])
def health_check():
    """健康檢查端點"""
    return {"status": "ok", "message": "API 運作正常"}
