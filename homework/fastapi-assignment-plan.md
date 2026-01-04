# 進階 Web 程式設計 - 自主學習作業計畫

## 📋 作業資訊

| 項目         | 內容                   |
| ------------ | ---------------------- |
| **課程**     | 進階 Web 程式設計      |
| **作業**     | 自主學習作業報告 (10%) |
| **選擇主題** | FAST API               |
| **繳交時間** | 自主學習週             |
| **完成狀態** | ✅ 已完成              |

---

## 🎯 作業目標

涵蓋老師教材中的三項內容：

| 主題               | 狀態 | 說明                                      |
| ------------------ | ---- | ----------------------------------------- |
| **FastAPI Basics** | ✅   | 路由、Path/Query Parameter、Pydantic 驗證 |
| **MySQL**          | ✅   | 資料庫連線、CRUD 操作、DBeaver 管理       |
| **Axios 呼叫 API** | ✅   | Next.js 前端整合、CORS 設定               |

---

## 📁 專案結構

```
homework/
├── fastapi-demo/
│   ├── backend/
│   │   ├── main.py              # FastAPI 主程式入口
│   │   ├── requirements.txt     # Python 依賴
│   │   ├── .venv/               # 虛擬環境
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── db.py            # MySQL 連線設定
│   │       └── job.py           # Job CRUD API
│   ├── frontend/
│   │   ├── app/
│   │   │   └── page.tsx         # Next.js 職缺管理頁面
│   │   └── package.json
│   └── README.md
└── fastapi-assignment-plan.md   # 本計畫文件
```

---

## 🔧 技術實作

### Backend - FastAPI

**main.py** - 主程式入口

- FastAPI 應用程式初始化
- CORS 中介軟體設定（允許 localhost:3001）
- Router 整合
- 根路由與健康檢查端點

**routers/db.py** - MySQL 連線

```python
def getDB():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password123",
        database="practice"
    )
```

**routers/job.py** - CRUD API

| 方法   | 端點            | 功能         |
| ------ | --------------- | ------------ |
| GET    | `/job/`         | 取得所有職缺 |
| GET    | `/job/{postid}` | 取得單一職缺 |
| POST   | `/job/`         | 新增職缺     |
| PUT    | `/job/{postid}` | 修改職缺     |
| DELETE | `/job/{postid}` | 刪除職缺     |

### Frontend - Next.js + Axios

**app/page.tsx** - 職缺管理頁面

```typescript
// Axios CRUD 範例
const API_URL = "http://127.0.0.1:8001";

// 讀取
const response = await axios.get(`${API_URL}/job/`);

// 新增
await axios.post(`${API_URL}/job/`, { company, content });

// 修改
await axios.put(`${API_URL}/job/${postid}`, { company, content });

// 刪除
await axios.delete(`${API_URL}/job/${postid}`);
```

### Database - MySQL (WSL)

**連線資訊**
| 項目 | 值 |
|------|-----|
| Host | localhost (WSL) / 172.18.101.176 (Windows) |
| Port | 3306 |
| Database | practice |
| User | admin |
| Password | admin123 |

---

## 📊 報告大綱 (PPT)

1. **主題介紹** - 為什麼選擇 FastAPI
2. **環境設定** - Python、FastAPI、MySQL、Node.js 安裝
3. **FastAPI 基礎** - 路由、參數、Pydantic 驗證
4. **MySQL 整合** - 連線設定、CRUD 操作、DBeaver 管理
5. **前端整合** - Next.js、Axios、CORS 設定
6. **Demo 展示** - 實際操作 CRUD 功能
7. **心得與結論**

---

## ✅ 執行步驟

### Step 1: 啟動 MySQL

```bash
sudo service mysql start
```

### Step 2: 啟動 Backend

```bash
cd homework/fastapi-demo/backend
source .venv/bin/activate
uvicorn main:app --reload --port 8001
```

### Step 3: 啟動 Frontend

```bash
cd homework/fastapi-demo/frontend
npm run dev -- --port 3001
```

### Step 4: 測試

| 項目       | URL                        |
| ---------- | -------------------------- |
| 前端頁面   | http://localhost:3001      |
| Swagger UI | http://127.0.0.1:8001/docs |

---

## 📸 建議截圖清單

### 程式碼

- [ ] `main.py` - FastAPI 主程式 + CORS 設定
- [ ] `routers/job.py` - CRUD API 程式碼
- [ ] `routers/db.py` - MySQL 連線設定
- [ ] `frontend/app/page.tsx` - Axios 呼叫程式碼

### Swagger UI

- [ ] API 文檔整體畫面
- [ ] GET /job 測試結果
- [ ] POST /job 測試結果

### 前端畫面

- [ ] 職缺列表頁面
- [ ] 新增職缺表單
- [ ] 修改/刪除操作

### DBeaver

- [ ] 連線成功畫面
- [ ] job 資料表內容
- [ ] 資料變化

---

## ✅ 完成驗證

| 功能          | 狀態 | 備註                           |
| ------------- | ---- | ------------------------------ |
| FastAPI 路由  | ✅   | main.py                        |
| Pydantic 驗證 | ✅   | JobCreate, JobUpdate           |
| MySQL 連線    | ✅   | db.py + mysql-connector-python |
| CRUD API      | ✅   | GET/POST/PUT/DELETE            |
| CORS 設定     | ✅   | 允許 localhost:3001            |
| Next.js 前端  | ✅   | app/page.tsx                   |
| Axios 呼叫    | ✅   | GET/POST/PUT/DELETE            |
| DBeaver 連線  | ✅   | WSL IP + admin 帳號            |

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
- [Next.js 官方文檔](https://nextjs.org/docs)
