from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DebateAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 開發用前端
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "DebateAI Backend is Running! 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
