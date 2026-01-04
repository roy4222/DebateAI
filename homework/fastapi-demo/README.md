# FastAPI Demo - 職缺管理系統

> 進階 Web 程式設計 - 自主學習作業

## 📋 專案說明

這個專案展示 FastAPI 的基本功能：

| 功能             | 說明                                          |
| ---------------- | --------------------------------------------- |
| **FastAPI 基礎** | 路由設定、Path/Query Parameter、Pydantic 驗證 |
| **MySQL 整合**   | 資料庫連線、CRUD 操作                         |
| **CORS 設定**    | 允許前端 Axios 呼叫                           |

---

## 🚀 快速開始

### Step 1: 準備 MySQL 資料庫

```sql
-- 建立資料庫
CREATE DATABASE IF NOT EXISTS practice;
USE practice;

-- 建立資料表
CREATE TABLE `job` (
  `postid` int(11) NOT NULL AUTO_INCREMENT,
  `company` varchar(45) NOT NULL,
  `content` text NOT NULL,
  `pdate` date NOT NULL,
  PRIMARY KEY (`postid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入測試資料
INSERT INTO `job` (`company`, `content`, `pdate`) VALUES
('Microsoft', '誠徵雲端工程師，三年工作經驗以上', '2024-10-18'),
('萬里雲', '誠徵雲端工程師，一年工作經驗以上', '2024-10-19'),
('Google', '誠徵雲端工程師，三年工作經驗以上', '2024-10-20'),
('AWS Taiwan', '誠徵雲端工程師，三年工作經驗以上', '2024-10-25'),
('伊雲谷', '誠徵雲端工程師，一年工作經驗以上', '2024-10-25'),
('叡揚資訊', '誠徵程式設計師，一年工作經驗以上', '2024-10-25');
```

### Step 2: 修改資料庫設定

編輯 `backend/routers/db.py`，修改連線參數：

```python
connection = mysql.connector.connect(
    host="localhost",
    user="root",          # 你的 MySQL 使用者名稱
    password="password",  # 你的 MySQL 密碼
    database="practice"
)
```

### Step 3: 安裝套件並啟動

```bash
cd backend

# 安裝套件
pip install -r requirements.txt

# 啟動伺服器
fastapi dev main.py
```

### Step 4: 測試 API

開啟瀏覽器：

- **Swagger UI**: http://localhost:8000/docs
- **API 根路由**: http://localhost:8000/

---

## 📡 API 端點

| 方法   | 端點            | 說明         |
| ------ | --------------- | ------------ |
| GET    | `/`             | Hello World  |
| GET    | `/health`       | 健康檢查     |
| GET    | `/job`          | 取得所有職缺 |
| GET    | `/job/{postid}` | 取得單一職缺 |
| POST   | `/job`          | 新增職缺     |
| PUT    | `/job/{postid}` | 修改職缺     |
| DELETE | `/job/{postid}` | 刪除職缺     |

---

## 🧪 驗證方式

### 方法 1: 使用 Swagger UI (推薦)

1. 啟動伺服器後，開啟 http://localhost:8000/docs
2. 點選任一 API → 「Try it out」→ 填入參數 → 「Execute」
3. 查看 Response 確認是否正確

### 方法 2: 使用 curl 指令

```bash
# 取得所有職缺
curl http://localhost:8000/job

# 取得單一職缺
curl http://localhost:8000/job/1

# 新增職缺
curl -X POST http://localhost:8000/job \
  -H "Content-Type: application/json" \
  -d '{"company": "Test", "content": "測試職缺"}'

# 修改職缺
curl -X PUT http://localhost:8000/job/1 \
  -H "Content-Type: application/json" \
  -d '{"company": "Updated Company"}'

# 刪除職缺
curl -X DELETE http://localhost:8000/job/1
```

---

## 📁 專案結構

```
fastapi-demo/
├── backend/
│   ├── main.py              # FastAPI 主程式
│   ├── requirements.txt     # Python 依賴
│   └── routers/
│       ├── __init__.py      # 模組初始化
│       ├── db.py            # MySQL 連線設定
│       └── job.py           # Job CRUD API
├── frontend/                # 前端 (Axios 範例)
│   └── ...
└── README.md
```
