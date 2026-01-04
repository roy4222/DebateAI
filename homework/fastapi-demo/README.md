# FastAPI Demo - 職缺管理系統

> 進階 Web 程式設計 - 自主學習作業

## 📋 專案說明

這個專案展示完整的 FullStack 開發：

| 技術        | 說明                                       |
| ----------- | ------------------------------------------ |
| **FastAPI** | Python Web 框架，路由、Pydantic 驗證、CORS |
| **MySQL**   | 資料庫連線、CRUD 操作                      |
| **Next.js** | React 前端框架                             |
| **Axios**   | HTTP 請求套件，呼叫 API                    |
| **DBeaver** | 資料庫管理工具                             |

---

## 🚀 快速開始

### Step 1: 啟動 MySQL (WSL)

```bash
sudo service mysql start
```

### Step 2: 啟動 Backend

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8001
```

### Step 3: 啟動 Frontend

```bash
cd frontend
npm run dev -- --port 3001
```

### Step 4: 開啟瀏覽器

| 服務           | URL                        |
| -------------- | -------------------------- |
| **前端頁面**   | http://localhost:3001      |
| **Swagger UI** | http://127.0.0.1:8001/docs |
| **API**        | http://127.0.0.1:8001      |

---

## 📡 API 端點

| 方法   | 端點            | 說明         |
| ------ | --------------- | ------------ |
| GET    | `/`             | Hello World  |
| GET    | `/health`       | 健康檢查     |
| GET    | `/job/`         | 取得所有職缺 |
| GET    | `/job/{postid}` | 取得單一職缺 |
| POST   | `/job/`         | 新增職缺     |
| PUT    | `/job/{postid}` | 修改職缺     |
| DELETE | `/job/{postid}` | 刪除職缺     |

---

## 🔧 MySQL 設定 (WSL)

### 初次安裝

```bash
# 安裝 MySQL
sudo apt update && sudo apt install -y mysql-server

# 啟動服務
sudo service mysql start

# 進入 MySQL 設定密碼
sudo mysql
```

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password123';
CREATE USER 'admin'@'%' IDENTIFIED BY 'admin123';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%';
FLUSH PRIVILEGES;

CREATE DATABASE practice;
USE practice;

CREATE TABLE job (
  postid INT AUTO_INCREMENT PRIMARY KEY,
  company VARCHAR(45) NOT NULL,
  content TEXT NOT NULL,
  pdate DATE NOT NULL
);

INSERT INTO job (company, content, pdate) VALUES
('Microsoft', '誠徵雲端工程師，三年工作經驗以上', '2024-10-18'),
('萬里雲', '誠徵雲端工程師，一年工作經驗以上', '2024-10-19'),
('Google', '誠徵雲端工程師，三年工作經驗以上', '2024-10-20'),
('AWS Taiwan', '誠徵雲端工程師，三年工作經驗以上', '2024-10-25'),
('伊雲谷', '誠徵雲端工程師，一年工作經驗以上', '2024-10-25'),
('叡揚資訊', '誠徵程式設計師，一年工作經驗以上', '2024-10-25');

EXIT;
```

### 允許 Windows 連線 (DBeaver)

```bash
# 修改 MySQL 綁定地址
sudo sed -i 's/bind-address\s*=\s*127.0.0.1/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo service mysql restart

# 取得 WSL IP
hostname -I | awk '{print $1}'
```

### DBeaver 連線設定

| 欄位        | 值                        |
| ----------- | ------------------------- |
| Server Host | `172.18.101.176` (WSL IP) |
| Port        | `3306`                    |
| Database    | `practice`                |
| Username    | `admin`                   |
| Password    | `admin123`                |

> ⚠️ 記得在 Driver properties 設定 `allowPublicKeyRetrieval = true`

---

## 📁 專案結構

```
fastapi-demo/
├── backend/
│   ├── main.py              # FastAPI 主程式
│   ├── requirements.txt     # Python 依賴
│   ├── .venv/               # Python 虛擬環境
│   └── routers/
│       ├── __init__.py      # 模組初始化
│       ├── db.py            # MySQL 連線設定
│       └── job.py           # Job CRUD API
├── frontend/
│   ├── app/
│   │   └── page.tsx         # Next.js 主頁面 (Axios CRUD)
│   ├── package.json
│   └── ...
└── README.md
```

---

## 🧪 測試 API

### 使用 curl

```bash
# 取得所有職缺
curl http://127.0.0.1:8001/job/

# 取得單一職缺
curl http://127.0.0.1:8001/job/1

# 新增職缺
curl -X POST http://127.0.0.1:8001/job/ \
  -H "Content-Type: application/json" \
  -d '{"company": "Test", "content": "測試職缺"}'

# 修改職缺
curl -X PUT http://127.0.0.1:8001/job/1 \
  -H "Content-Type: application/json" \
  -d '{"company": "Updated Company"}'

# 刪除職缺
curl -X DELETE http://127.0.0.1:8001/job/1
```

---

## ✅ 功能驗證結果

| 功能            | 狀態    |
| --------------- | ------- |
| GET 所有職缺    | ✅ 成功 |
| GET 單一職缺    | ✅ 成功 |
| POST 新增職缺   | ✅ 成功 |
| PUT 修改職缺    | ✅ 成功 |
| DELETE 刪除職缺 | ✅ 成功 |
| MySQL 連線      | ✅ 成功 |
| DBeaver 連線    | ✅ 成功 |
| Frontend CRUD   | ✅ 成功 |
