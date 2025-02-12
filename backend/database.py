import sqlite3
import datetime
from collections import defaultdict

DATABASE_PATH = "documents.db"

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            predicted_category TEXT NOT NULL,
            confidence FLOAT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# 插入新文件记录
def insert_document(filename, predicted_category, confidence, upload_time):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO documents (filename, predicted_category, confidence, upload_time)
        VALUES (?, ?, ?, ?)
    """, (filename, predicted_category, confidence, upload_time))
    
    conn.commit()
    conn.close()

# 获取所有文件记录
def get_all_documents():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT filename, predicted_category, confidence, upload_time FROM documents ORDER BY upload_time DESC")
    rows = cursor.fetchall()
    
    conn.close()
    
    return [
        {
            "filename": row[0],
            "predicted_category": row[1],
            "confidence": row[2],
            "upload_time": row[3]
        }
        for row in rows
    ]

# 获取文档类别分布
def get_document_distribution():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT predicted_category, COUNT(*) FROM documents GROUP BY predicted_category")
    rows = cursor.fetchall()
    
    conn.close()
    
    categories = [row[0] for row in rows]
    counts = [row[1] for row in rows]
    
    return {"categories": categories, "counts": counts}

# 获取上传趋势
def get_upload_trends():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DATE(upload_time) as upload_date, COUNT(*) FROM documents GROUP BY upload_date ORDER BY upload_date")
    rows = cursor.fetchall()
    
    conn.close()
    
    upload_times = {row[0]: row[1] for row in rows}
    return upload_times

# 获取置信度分布
def get_confidence_distribution():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT confidence FROM documents")
    rows = cursor.fetchall()
    
    conn.close()
    
    confidence_scores = [row[0] for row in rows]
    return confidence_scores

# 运行数据库初始化
init_db()