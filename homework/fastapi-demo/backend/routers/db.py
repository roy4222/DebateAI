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
            user="root",          # 請改成你的 MySQL 使用者名稱
            password="",          # 請改成你的 MySQL 密碼
            database="practice"   # 請改成你的資料庫名稱
        )
        return connection
    except Error as e:
        print(f"資料庫連線錯誤: {e}")
        raise e
