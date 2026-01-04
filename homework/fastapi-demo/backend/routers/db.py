"""
MySQL 資料庫連線設定

使用前請確認：
1. 已安裝 MySQL
2. 已建立 practice 資料庫
3. 已建立 job 資料表 (參考 README.md 的 SQL)
4. 修改下方的連線參數
"""
import mysql.connector
from mysql.connector import Error


def getDB():
    """取得 MySQL 資料庫連線"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password123",  # 已設定的密碼
            database="practice"
        )
        return connection
    except Error as e:
        print(f"資料庫連線錯誤: {e}")
        raise e
