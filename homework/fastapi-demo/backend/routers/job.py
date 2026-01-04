"""
Job CRUD API - 職缺管理 API

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
from routers.db import getDB

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


class JobResponse(BaseModel):
    """回應職缺資料的模型"""
    postid: int
    company: str
    content: str
    pdate: date


# ========== READ ==========

@router.get("/")
async def get_jobs(skip: int = 0, limit: int = 50):
    """
    取得所有職缺
    
    - **skip**: 跳過幾筆 (用於分頁)
    - **limit**: 取得幾筆 (預設 50)
    """
    mydb = getDB()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM job LIMIT %s OFFSET %s", (limit, skip))
    result = mycursor.fetchall()
    mydb.close()
    return result


@router.get("/{postid}")
async def get_job(postid: int):
    """
    取得單一職缺
    
    - **postid**: 職缺編號
    """
    mydb = getDB()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM job WHERE postid = %s", (postid,))
    result = mycursor.fetchone()
    mydb.close()
    
    if result is None:
        raise HTTPException(status_code=404, detail=f"找不到職缺編號 {postid}")
    
    return result


# ========== CREATE ==========

@router.post("/")
async def create_job(job: JobCreate):
    """
    新增職缺
    
    Request Body:
    - **company**: 公司名稱
    - **content**: 職缺內容
    """
    mydb = getDB()
    mycursor = mydb.cursor()
    sql = "INSERT INTO job (company, content, pdate) VALUES (%s, %s, CURDATE())"
    mycursor.execute(sql, (job.company, job.content))
    mydb.commit()
    
    # 取得新增的 ID
    new_id = mycursor.lastrowid
    mydb.close()
    
    return {"message": "新增成功", "postid": new_id}


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
    mydb = getDB()
    mycursor = mydb.cursor(dictionary=True)
    
    # 先檢查資料是否存在
    mycursor.execute("SELECT * FROM job WHERE postid = %s", (postid,))
    existing = mycursor.fetchone()
    
    if existing is None:
        mydb.close()
        raise HTTPException(status_code=404, detail=f"找不到職缺編號 {postid}")
    
    # 更新資料 (只更新有提供的欄位)
    update_fields = []
    values = []
    
    if job.company is not None:
        update_fields.append("company = %s")
        values.append(job.company)
    
    if job.content is not None:
        update_fields.append("content = %s")
        values.append(job.content)
    
    if update_fields:
        sql = f"UPDATE job SET {', '.join(update_fields)} WHERE postid = %s"
        values.append(postid)
        mycursor.execute(sql, tuple(values))
        mydb.commit()
    
    mydb.close()
    return {"message": "修改成功", "postid": postid}


# ========== DELETE ==========

@router.delete("/{postid}")
async def delete_job(postid: int):
    """
    刪除職缺
    
    - **postid**: 職缺編號
    """
    mydb = getDB()
    mycursor = mydb.cursor()
    
    # 先檢查資料是否存在
    mycursor.execute("SELECT postid FROM job WHERE postid = %s", (postid,))
    existing = mycursor.fetchone()
    
    if existing is None:
        mydb.close()
        raise HTTPException(status_code=404, detail=f"找不到職缺編號 {postid}")
    
    # 刪除資料
    mycursor.execute("DELETE FROM job WHERE postid = %s", (postid,))
    mydb.commit()
    mydb.close()
    
    return {"message": "刪除成功", "postid": postid}
