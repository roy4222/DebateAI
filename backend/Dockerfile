# 使用 uv 官方映像
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# 1. 複製依賴檔案 (包含 README.md 以避免 hatchling 報錯)
COPY pyproject.toml uv.lock* README.md ./

# 2. 安裝依賴
RUN uv sync --frozen --no-dev

# 3. 複製程式碼
COPY app ./app

# 4. 暴露 Port
EXPOSE 8080

# 5. 啟動指令 (明確指定 Port 8080)
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]