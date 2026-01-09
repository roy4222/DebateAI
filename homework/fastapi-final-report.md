# 進階 Web 程式設計 - 自主學習作業報告

**課程名稱**：進階 Web 程式設計  
**作業主題**：FastAPI 全端開發實作 (自主學習)  
**學生姓名**：盧柏宇  
**學號**：412401355  
**班級**：資管三甲  
**繳交日期**：2026 年 1 月

---

## 1. 主題選定與學習目標

本次自主學習作業選擇 **FastAPI** 作為主題，目標是整合本學期所接觸的技術，完成一個具備完整 CRUD 功能的「職缺管理系統」。

### 學習重點

根據課程要求，本報告將涵蓋以下三個核心實作部分：

1.  **FastAPI Basics**：建立 RESTful API，包含路由設定、參數處理與 Pydantic 資料驗證。
2.  **MySQL**：使用 Python 連接 MySQL 資料庫，進行持久化的資料存取。
3.  **透過 Axios 呼叫 API**：在前端 (Next.js) 使用 Axios 與後端進行非同步資料交換。

---

## 2. 開發環境與工具

為了實作此系統，我搭建了以下開發環境：

- **後端框架**: FastAPI (Python 3.12)
- **資料庫**: MySQL 8.0 (運行於 WSL2)
- **前端框架**: Next.js 16 (React)
- **API 工具**: Axios (HTTP Client), Swagger UI (測試文件)
- **管理工具**: DBeaver (資料庫管理)

> **[請在此處插入截圖 1：開發環境全覽]** > _建議畫面：VS Code 打開專案結構的畫面，或是終端機同時運行前後端的畫面。_

---

## 3. 實作細節 (Implementation)

### 3.1 Part 1: FastAPI Basics (基礎與路由)

FastAPI 的核心優勢在於快速建立與自動驗證。我在 `main.py` 與 `routers/job.py` 中實作了符合 RESTful 標準的路由。

**關鍵程式碼說明：**
建立了一個 `JobCreate` 的 Pydantic 模型，確保前端傳來的 `company` 與 `content` 必定為字串且不為空。

```python
# Pydantic 模型定義
class JobCreate(BaseModel):
    company: str
    content: str
```

**API 路由實作：**

- `GET /job/`：讀取所有資料
- `POST /job/`：新增資料

> **[請在此處插入截圖 2：Swagger UI 自動生成文件]** > _建議畫面：瀏覽器開啟 `http://127.0.0.1:8001/docs` 的畫面，展開 /job/ 的 GET 或 POST 區塊，證明 API 路由已建立。_

### 3.2 Part 2: MySQL (資料庫整合)

資料庫部分使用 `mysql-connector-python` 套件進行連線。我在 MySQL 中建立了一個 `job` 資料表，包含 `postid` (主鍵)、`company`、`content` 與 `pdate`。

**資料庫連線程式碼 (db.py)：**
封裝了 `getDB()` 函式，確保每次 API 呼叫都能正確取得連線並在結束後關閉。

```python
def getDB():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password123",
        database="practice"
    )
```

> **[請在此處插入截圖 3：DBeaver 資料庫資料]** > _建議畫面：開啟 DBeaver，顯示 `job` 資料表的內容，證明資料已成功寫入資料庫（例如看到幾筆測試的職缺資料）。_

### 3.3 Part 3: 透過 Axios 呼叫 API (前端整合)

在 Next.js 前端頁面中，我使用 `axios` 來取代傳統的 fetch，這讓 HTTP 請求的處理變得更簡潔。

**前端實作重點：**

1.  **解決 CORS 問題**：在後端 `main.py` 加入了 `CORSMiddleware`，允許來自 `localhost:3001` 的請求。
2.  **Axios 非同步呼叫**：

```typescript
// 前端 page.tsx 使用 Axios 取得資料
async function fetchJobs() {
  try {
    const response = await axios.get("http://127.0.0.1:8001/job/");
    setJobs(response.data);
  } catch (error) {
    console.error("無法取得職缺資料", error);
  }
}
```

> **[請在此處插入截圖 4：前端職缺列表頁面]** > _建議畫面：瀏覽器開啟 `http://localhost:3001` 的前端網頁，顯示出從後端抓取回來的職缺列表表格。_

> **[請在此處插入截圖 5：前端新增/修改功能操作]** > _建議畫面：展示按下「新增」或「刪除」按鈕後的結果，或是在 Console 中印出的 Axios 請求成功訊息。_

---

## 4. 學習心得與結論

透過這次自主學習，我成功將 FastAPI 與 MySQL、Next.js 串接起來。特別是在「透過 Axios 呼叫 API」的部分，深刻體會到前後端分離開發中，CORS 設定與 API 格式約定的重要性。FastAPI 提供的自動化文件 (Swagger UI) 也大大加速了我的開發測試流程，是一個非常現代且高效的 Web 開發框架。

---

**參考資料：**

1. [Notion] FAST API Basics
2. [Notion] MySQL Integration
3. [Notion] 透過 Axios 呼叫 API
