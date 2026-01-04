# 進階 Web 程式設計 - 自主學習作業報告

---

**課程名稱**：進階 Web 程式設計  
**作業主題**：FastAPI  
**學生姓名**：盧柏宇  
**學號**：412401355  
**班級**：資管三甲  
**繳交日期**：2026 年 1 月

---

## 目錄

1. 主題介紹
2. 開發環境
3. 系統架構
4. Backend 實作 - FastAPI
5. Database 實作 - MySQL
6. Frontend 實作 - Next.js + Axios
7. 功能展示
8. 心得與結論
9. 參考資料

---

## 1. 主題介紹

### 1.1 為什麼選擇 FastAPI？

FastAPI 是一個現代、高效能的 Python Web 框架，專為建立 API 而設計。相較於其他框架（如 Flask、Django），FastAPI 具有以下優勢：

| 特點           | 說明                                               |
| -------------- | -------------------------------------------------- |
| **高效能**     | 基於 Starlette 和 Pydantic，效能接近 Node.js 和 Go |
| **自動文檔**   | 內建 Swagger UI 和 ReDoc，自動產生 API 文檔        |
| **型別驗證**   | 使用 Pydantic 進行資料驗證，減少 Bug               |
| **簡潔語法**   | 使用 Python 型別提示，程式碼簡潔易讀               |
| **非同步支援** | 原生支援 async/await，適合高併發場景               |

### 1.2 專案目標

本專案實作一個「職缺管理系統」，涵蓋老師教材中的三大主題：

1. **FastAPI 基礎** - 路由設定、Path/Query Parameter、Pydantic 驗證
2. **MySQL 整合** - 資料庫連線、CRUD 操作
3. **Axios 呼叫 API** - 前端整合、CORS 設定

---

## 2. 開發環境

### 2.1 使用工具

| 工具    | 版本         | 用途           |
| ------- | ------------ | -------------- |
| Python  | 3.12         | 後端程式語言   |
| FastAPI | 0.115+       | Web API 框架   |
| Uvicorn | 0.34+        | ASGI 伺服器    |
| MySQL   | 8.0.44       | 關聯式資料庫   |
| Node.js | 22+          | 前端執行環境   |
| Next.js | 16.1         | React 框架     |
| Axios   | 1.7+         | HTTP 請求套件  |
| DBeaver | 25.3.1       | 資料庫管理工具 |
| WSL2    | Ubuntu 24.04 | Linux 開發環境 |

### 2.2 安裝指令

**Backend 套件安裝**

```bash
pip install fastapi uvicorn mysql-connector-python pydantic
```

**Frontend 套件安裝**

```bash
npm install axios
```

---

## 3. 系統架構

### 3.1 三層式架構

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend                               │
│                 (Next.js + Axios)                           │
│                  http://localhost:3001                       │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP (GET/POST/PUT/DELETE)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                       Backend                                │
│                 (FastAPI + Uvicorn)                         │
│                  http://127.0.0.1:8001                       │
└─────────────────────────┬───────────────────────────────────┘
                          │ MySQL Connector
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                       Database                               │
│                    (MySQL 8.0)                               │
│                  localhost:3306                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 專案結構

```
fastapi-demo/
├── backend/
│   ├── main.py              # FastAPI 主程式
│   ├── requirements.txt     # Python 依賴
│   └── routers/
│       ├── __init__.py      # 模組初始化
│       ├── db.py            # MySQL 連線設定
│       └── job.py           # Job CRUD API
├── frontend/
│   ├── app/
│   │   └── page.tsx         # 職缺管理頁面
│   └── package.json
└── README.md
```

---

## 4. Backend 實作 - FastAPI

### 4.1 主程式 (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import job

# 建立 FastAPI 應用程式
app = FastAPI(
    title="Job API - 徵才系統",
    description="進階Web程式設計 - 自主學習作業 Demo",
    version="1.0.0"
)

# CORS 設定 - 允許前端呼叫
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 引入 Job Router
app.include_router(job.router)

# 根路由
@app.get("/")
async def root():
    return {"message": "歡迎使用 Job API - 徵才系統"}

# 健康檢查
@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

**重點說明**：

- `FastAPI()` 建立應用程式實例，可設定標題和描述
- `CORSMiddleware` 允許跨網域請求，解決前端呼叫 API 的問題
- `include_router()` 將 API 路由模組化管理

### 4.2 CRUD API (job.py)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from .db import getDB

router = APIRouter(prefix="/job", tags=["職缺管理"])

# Pydantic 模型 - 資料驗證
class JobCreate(BaseModel):
    company: str
    content: str

class JobUpdate(BaseModel):
    company: Optional[str] = None
    content: Optional[str] = None

# GET - 取得所有職缺
@router.get("/")
async def get_jobs(skip: int = 0, limit: int = 50):
    mydb = getDB()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM job LIMIT %s OFFSET %s", (limit, skip))
    result = mycursor.fetchall()
    mydb.close()
    return result

# GET - 取得單一職缺
@router.get("/{postid}")
async def get_job(postid: int):
    mydb = getDB()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM job WHERE postid = %s", (postid,))
    result = mycursor.fetchone()
    mydb.close()
    if result is None:
        raise HTTPException(status_code=404, detail=f"找不到職缺編號 {postid}")
    return result

# POST - 新增職缺
@router.post("/")
async def create_job(job: JobCreate):
    mydb = getDB()
    mycursor = mydb.cursor()
    sql = "INSERT INTO job (company, content, pdate) VALUES (%s, %s, CURDATE())"
    mycursor.execute(sql, (job.company, job.content))
    mydb.commit()
    new_id = mycursor.lastrowid
    mydb.close()
    return {"message": "新增成功", "postid": new_id}

# PUT - 修改職缺
@router.put("/{postid}")
async def update_job(postid: int, job: JobUpdate):
    mydb = getDB()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM job WHERE postid = %s", (postid,))
    if mycursor.fetchone() is None:
        mydb.close()
        raise HTTPException(status_code=404, detail=f"找不到職缺編號 {postid}")

    if job.company:
        mycursor.execute("UPDATE job SET company = %s WHERE postid = %s", (job.company, postid))
    if job.content:
        mycursor.execute("UPDATE job SET content = %s WHERE postid = %s", (job.content, postid))
    mydb.commit()
    mydb.close()
    return {"message": "修改成功", "postid": postid}

# DELETE - 刪除職缺
@router.delete("/{postid}")
async def delete_job(postid: int):
    mydb = getDB()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT postid FROM job WHERE postid = %s", (postid,))
    if mycursor.fetchone() is None:
        mydb.close()
        raise HTTPException(status_code=404, detail=f"找不到職缺編號 {postid}")

    mycursor.execute("DELETE FROM job WHERE postid = %s", (postid,))
    mydb.commit()
    mydb.close()
    return {"message": "刪除成功", "postid": postid}
```

**重點說明**：

- `APIRouter` 將相關 API 群組化，設定 prefix 和 tags
- `Pydantic BaseModel` 自動驗證請求資料格式
- `HTTPException` 回傳適當的 HTTP 錯誤碼

### 4.3 API 端點總覽

| 方法   | 端點            | 功能         | 參數                                  |
| ------ | --------------- | ------------ | ------------------------------------- |
| GET    | `/job/`         | 取得所有職缺 | skip, limit (Query)                   |
| GET    | `/job/{postid}` | 取得單一職缺 | postid (Path)                         |
| POST   | `/job/`         | 新增職缺     | company, content (Body)               |
| PUT    | `/job/{postid}` | 修改職缺     | postid (Path), company/content (Body) |
| DELETE | `/job/{postid}` | 刪除職缺     | postid (Path)                         |

---

## 5. Database 實作 - MySQL

### 5.1 資料庫連線 (db.py)

```python
import mysql.connector
from mysql.connector import Error

def getDB():
    """取得 MySQL 資料庫連線"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password123",
            database="practice"
        )
        return connection
    except Error as e:
        print(f"資料庫連線錯誤: {e}")
        raise e
```

### 5.2 資料表結構

```sql
CREATE DATABASE practice;
USE practice;

CREATE TABLE job (
  postid INT AUTO_INCREMENT PRIMARY KEY,
  company VARCHAR(45) NOT NULL,
  content TEXT NOT NULL,
  pdate DATE NOT NULL
);
```

| 欄位    | 型別        | 說明           |
| ------- | ----------- | -------------- |
| postid  | INT         | 主鍵，自動遞增 |
| company | VARCHAR(45) | 公司名稱       |
| content | TEXT        | 職缺內容       |
| pdate   | DATE        | 發布日期       |

### 5.3 測試資料

```sql
INSERT INTO job (company, content, pdate) VALUES
('Microsoft', '誠徵雲端工程師，三年工作經驗以上', '2024-10-18'),
('萬里雲', '誠徵雲端工程師，一年工作經驗以上', '2024-10-19'),
('Google', '誠徵雲端工程師，三年工作經驗以上', '2024-10-20'),
('AWS Taiwan', '誠徵雲端工程師，三年工作經驗以上', '2024-10-25'),
('伊雲谷', '誠徵雲端工程師，一年工作經驗以上', '2024-10-25'),
('叡揚資訊', '誠徵程式設計師，一年工作經驗以上', '2024-10-25');
```

---

## 6. Frontend 實作 - Next.js + Axios

### 6.1 主頁面 (page.tsx)

```typescript
"use client";
import { useState, useEffect } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8001";

interface Job {
  postid: number;
  company: string;
  content: string;
  pdate: string;
}

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);

  // 讀取所有職缺 (GET)
  async function fetchJobs() {
    const response = await axios.get(`${API_URL}/job/`);
    setJobs(response.data);
  }

  // 新增職缺 (POST)
  async function createJob(company: string, content: string) {
    await axios.post(`${API_URL}/job/`, { company, content });
    fetchJobs(); // 重新載入
  }

  // 修改職缺 (PUT)
  async function updateJob(postid: number, company: string, content: string) {
    await axios.put(`${API_URL}/job/${postid}`, { company, content });
    fetchJobs(); // 重新載入
  }

  // 刪除職缺 (DELETE)
  async function deleteJob(postid: number) {
    await axios.delete(`${API_URL}/job/${postid}`);
    fetchJobs(); // 重新載入
  }

  useEffect(() => {
    fetchJobs();
  }, []);

  return (
    <main>
      <h1>職缺管理系統</h1>
      {/* 職缺列表 */}
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>公司</th>
            <th>內容</th>
            <th>日期</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.postid}>
              <td>{job.postid}</td>
              <td>{job.company}</td>
              <td>{job.content}</td>
              <td>{job.pdate}</td>
              <td>
                <button
                  onClick={() => updateJob(job.postid, "新公司", "新內容")}
                >
                  修改
                </button>
                <button onClick={() => deleteJob(job.postid)}>刪除</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
```

**重點說明**：

- `axios.get()` 發送 GET 請求取得資料
- `axios.post()` 發送 POST 請求新增資料
- `axios.put()` 發送 PUT 請求修改資料
- `axios.delete()` 發送 DELETE 請求刪除資料
- `useEffect()` 在頁面載入時自動取得職缺列表

---

## 7. 功能展示

### 7.1 Swagger UI

FastAPI 內建 Swagger UI，可在瀏覽器開啟 `http://127.0.0.1:8001/docs` 測試 API。

**（請插入 Swagger UI 截圖）**

### 7.2 前端頁面

職缺管理頁面提供完整的 CRUD 功能。

**（請插入前端頁面截圖）**

### 7.3 DBeaver 資料庫

使用 DBeaver 連接 MySQL，可查看資料變化。

**（請插入 DBeaver 截圖）**

### 7.4 測試結果

| 功能            | 測試結果 |
| --------------- | -------- |
| GET 所有職缺    | ✅ 成功  |
| GET 單一職缺    | ✅ 成功  |
| POST 新增職缺   | ✅ 成功  |
| PUT 修改職缺    | ✅ 成功  |
| DELETE 刪除職缺 | ✅ 成功  |
| MySQL 連線      | ✅ 成功  |
| DBeaver 連線    | ✅ 成功  |
| 前端 CRUD       | ✅ 成功  |

---

## 8. 心得與結論

### 8.1 學習心得

透過本次自主學習，我對 FastAPI 有了更深入的了解：

1. **FastAPI 的便利性** - 相比 Flask，FastAPI 的語法更簡潔，內建的 Swagger UI 讓 API 測試變得非常方便。

2. **Pydantic 驗證** - 使用 Pydantic BaseModel 定義資料格式，可以自動驗證請求資料，減少手動檢查的程式碼。

3. **CORS 設定** - 了解跨網域請求的原理，以及如何正確設定 CORSMiddleware。

4. **前後端分離** - 實際體驗前後端分離的開發流程，前端透過 Axios 呼叫 API，後端專注於資料處理。

### 8.2 遇到的問題與解決方式

| 問題                       | 解決方式                                                  |
| -------------------------- | --------------------------------------------------------- |
| CORS 錯誤                  | 在 FastAPI 加入 CORSMiddleware，允許前端網域              |
| MySQL 連線失敗             | 確認服務已啟動 (`sudo service mysql start`)               |
| DBeaver 無法連線 WSL MySQL | 使用 WSL IP 地址，並設定 `allowPublicKeyRetrieval = true` |

### 8.3 結論

FastAPI 是一個非常適合用於 API 開發的框架，其高效能、自動文檔、型別驗證等特性，讓開發效率大幅提升。結合 MySQL 和 Next.js，可以快速建立完整的全端應用程式。

---

## 9. 參考資料

1. FastAPI 官方文檔 - https://fastapi.tiangolo.com/
2. MySQL Connector Python - https://dev.mysql.com/doc/connector-python/en/
3. Axios 官方文檔 - https://axios-http.com/
4. Next.js 官方文檔 - https://nextjs.org/docs
5. Pydantic 官方文檔 - https://docs.pydantic.dev/

---

**（報告結束）**
