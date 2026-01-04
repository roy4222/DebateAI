"""
Job CRUD API - 記憶體版本 (不需要 MySQL)

這個版本使用 Python List 儲存資料，重啟後資料會消失。
適合用來測試和驗證 API 是否正常運作。

提供完整的 CRUD 操作：
- GET /job - 取得所有職缺
- GET /job/{postid} - 取得單一職缺
- POST /job - 新增職缺
- PUT /job/{postid} - 修改職缺
- DELETE /job/{postid} - 刪除職缺
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter(prefix="/job", tags=["Job API"])


# Pydantic Model - 用於資料驗證
class JobCreate(BaseModel):
    """新增職缺時使用的模型"""
    company: str
    content: str


class JobUpdate(BaseModel):
    """修改職缺時使用的模型"""
    company: Optional[str] = None
    content: Optional[str] = None


class Job(BaseModel):
    """職缺資料模型"""
    postid: int
    company: str
    content: str
    pdate: str


# ========== 記憶體資料儲存 ==========
# 用 List 儲存職缺資料，重啟後會重置
jobs_db: list[Job] = [
    Job(postid=1, company="Microsoft", content="誠徵雲端工程師，三年工作經驗以上", pdate="2024-10-18"),
    Job(postid=2, company="萬里雲", content="誠徵雲端工程師，一年工作經驗以上", pdate="2024-10-19"),
    Job(postid=3, company="Google", content="誠徵雲端工程師，三年工作經驗以上", pdate="2024-10-20"),
    Job(postid=4, company="AWS Taiwan", content="誠徵雲端工程師，三年工作經驗以上", pdate="2024-10-25"),
    Job(postid=5, company="伊雲谷", content="誠徵雲端工程師，一年工作經驗以上", pdate="2024-10-25"),
    Job(postid=6, company="叡揚資訊", content="誠徵程式設計師，一年工作經驗以上", pdate="2024-10-25"),
]

# 自動遞增 ID 計數器
next_id = 7


# ========== READ ==========

@router.get("/")
async def get_jobs(skip: int = 0, limit: int = 50):
    """
    取得所有職缺
    
    - **skip**: 跳過幾筆 (用於分頁)
    - **limit**: 取得幾筆 (預設 50)
    """
    return jobs_db[skip:skip + limit]


@router.get("/{postid}")
async def get_job(postid: int):
    """
    取得單一職缺
    
    - **postid**: 職缺編號
    """
    for job in jobs_db:
        if job.postid == postid:
            return job
    
    raise HTTPException(status_code=404, detail=f"找不到職缺編號 {postid}")


# ========== CREATE ==========

@router.post("/")
async def create_job(job: JobCreate):
    """
    新增職缺
    
    Request Body:
    - **company**: 公司名稱
    - **content**: 職缺內容
    """
    global next_id
    
    new_job = Job(
        postid=next_id,
        company=job.company,
        content=job.content,
        pdate=str(date.today())
    )
    jobs_db.append(new_job)
    next_id += 1
    
    return {"message": "新增成功", "postid": new_job.postid}


# ========== UPDATE ==========

@router.put("/{postid}")
async def update_job(postid: int, job: JobUpdate):
    """
    修改職缺
    
    - **postid**: 職缺編號
    
    Request Body:
    - **company**: 公司名稱 (可選)
    - **content**: 職缺內容 (可選)
    """
    for i, existing_job in enumerate(jobs_db):
        if existing_job.postid == postid:
            # 更新有提供的欄位
            if job.company is not None:
                jobs_db[i] = Job(
                    postid=existing_job.postid,
                    company=job.company,
                    content=existing_job.content if job.content is None else job.content,
                    pdate=existing_job.pdate
                )
            elif job.content is not None:
                jobs_db[i] = Job(
                    postid=existing_job.postid,
                    company=existing_job.company,
                    content=job.content,
                    pdate=existing_job.pdate
                )
            return {"message": "修改成功", "postid": postid}
    
    raise HTTPException(status_code=404, detail=f"找不到職缺編號 {postid}")


# ========== DELETE ==========

@router.delete("/{postid}")
async def delete_job(postid: int):
    """
    刪除職缺
    
    - **postid**: 職缺編號
    """
    for i, job in enumerate(jobs_db):
        if job.postid == postid:
            jobs_db.pop(i)
            return {"message": "刪除成功", "postid": postid}
    
    raise HTTPException(status_code=404, detail=f"找不到職缺編號 {postid}")
