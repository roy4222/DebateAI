# 進階 Web 程式設計 - 自主學習作業計畫

## 📋 作業資訊

| 項目         | 內容                   |
| ------------ | ---------------------- |
| **課程**     | 進階 Web 程式設計      |
| **作業**     | 自主學習作業報告 (10%) |
| **選擇主題** | FAST API               |
| **繳交時間** | 自主學習週             |

---

## 🎯 作業目標

涵蓋老師教材中的三項內容：

1. **FastAPI Basics** - 基本路由、參數處理、Pydantic 驗證
2. **MySQL** - 資料庫連線與 CRUD 操作
3. **Axios 呼叫 API** - 前端整合與 CORS 設定

---

## 📁 專案結構

```
homework/
├── fastapi-demo/
│   ├── backend/
│   │   ├── main.py              # FastAPI 主程式入口
│   │   ├── requirements.txt     # Python 依賴
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── db.py            # MySQL 連線設定
│   │       └── job.py           # Job CRUD API
│   └── frontend/
│       ├── package.json
│       └── src/
│           └── JobList.tsx      # Axios CRUD 範例
└── fastapi-assignment-plan.md   # 本計畫文件
```

---

## 🔧 Backend 實作內容

### 1. FastAPI 基礎 (`main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import job

app = FastAPI()

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(job.router)

@app.get("/")
def root():
    return {"message": "Hello FastAPI"}
```

### 2. MySQL 連線 (`routers/db.py`)

```python
import mysql.connector

def getDB():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="practice"
    )
```

### 3. Job CRUD API (`routers/job.py`)

| 方法   | 端點        | 功能         |
| ------ | ----------- | ------------ |
| GET    | `/job`      | 取得所有職缺 |
| GET    | `/job/{id}` | 取得單一職缺 |
| POST   | `/job`      | 新增職缺     |
| PUT    | `/job/{id}` | 修改職缺     |
| DELETE | `/job/{id}` | 刪除職缺     |

---

## 🖥️ Frontend 實作內容

### Axios CRUD 範例

```typescript
// 讀取
const response = await axios.get("http://localhost:8000/job");

// 新增
await axios.post("http://localhost:8000/job", newJob);

// 修改
await axios.put(`http://localhost:8000/job/${id}`, updatedJob);

// 刪除
await axios.delete(`http://localhost:8000/job/${id}`);
```

---

## 📊 報告大綱 (如需要 PPT)

1. **主題介紹** - 為什麼選擇 FastAPI
2. **環境設定** - Python、FastAPI、MySQL 安裝
3. **FastAPI 基礎** - 路由、參數、Pydantic
4. **MySQL 整合** - 連線、CRUD 操作
5. **前端整合** - Axios、useEffect、CORS
6. **Demo 展示** - 實際操作 CRUD 功能
7. **心得與結論**

---

## ✅ 執行步驟

### Step 1: 準備資料庫

```sql
CREATE TABLE job (
  postid INT AUTO_INCREMENT PRIMARY KEY,
  company VARCHAR(45) NOT NULL,
  content TEXT NOT NULL,
  pdate DATE NOT NULL
);

INSERT INTO job (company, content, pdate) VALUES
('Microsoft', '誠徵雲端工程師，三年經驗以上', '2024-10-18'),
('Google', '誠徵後端工程師，兩年經驗以上', '2024-10-19');
```

### Step 2: 啟動 Backend

```bash
cd homework/fastapi-demo/backend
pip install -r requirements.txt
fastapi dev main.py
```

### Step 3: 啟動 Frontend

```bash
cd homework/fastapi-demo/frontend
npm install
npm run dev
```

### Step 4: 測試 API

- Swagger UI: http://localhost:8000/docs
- 前端頁面: http://localhost:3000

---

## 📌 待確認事項

- [ ] 老師確認繳交格式 (PPT/Word/程式碼)
- [ ] 老師確認是否需要口頭報告
- [ ] 老師確認繳交期限

---

## 🔗 參考資源

- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [MySQL Connector Python](https://dev.mysql.com/doc/connector-python/en/)
- [Axios 官方文檔](https://axios-http.com/)
