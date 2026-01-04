"""
FastAPI Demo - 記憶體版本 (不需要 MySQL)

這個版本使用記憶體儲存資料，不需要安裝 MySQL。
適合用來快速測試和驗證 API 是否正常運作。

啟動方式：
    fastapi dev main_memory.py

測試 API：
    http://localhost:8000/docs (Swagger UI)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import job_memory

# 建立 FastAPI 應用程式
app = FastAPI(
    title="Job API - 徵才系統 (記憶體版)",
    description="進階Web程式設計 - 自主學習作業 Demo (不需要 MySQL)",
    version="1.0.0"
)

# ========== CORS 設定 ==========
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 引入 Router ==========
app.include_router(job_memory.router)


# ========== 根路由 ==========
@app.get("/", tags=["Root"])
def root():
    """API 根路由 - Hello World"""
    return {"message": "Hello FastAPI! 這是記憶體版本，不需要 MySQL"}


@app.get("/health", tags=["Root"])
def health_check():
    """健康檢查端點"""
    return {"status": "ok", "message": "API 運作正常 (記憶體版)"}
