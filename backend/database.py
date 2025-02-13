import sqlite3
import datetime
from collections import defaultdict

DATABASE_PATH = "documents.db"

# database initialization
def init_db():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    #Create the documents table if it doesn't exist
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

# Insert a new document record into the database
def insert_document(filename, predicted_category, confidence, upload_time):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO documents (filename, predicted_category, confidence, upload_time)
        VALUES (?, ?, ?, ?)
    """, (filename, predicted_category, confidence, upload_time))
    
    conn.commit()
    conn.close()

# Retrieve all document records from the database
def get_all_documents():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT filename, predicted_category, confidence, upload_time FROM documents ORDER BY upload_time DESC")
    rows = cursor.fetchall()
    
    conn.close()
    
    # Format the results into a list of dictionaries
    return [
        {
            "filename": row[0],
            "predicted_category": row[1],
            "confidence": row[2],
            "upload_time": row[3]
        }
        for row in rows
    ]

# Retrieve the distribution of document categories
def get_document_distribution():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT predicted_category, COUNT(*) FROM documents GROUP BY predicted_category")
    rows = cursor.fetchall()
    
    conn.close()
    
    categories = [row[0] for row in rows]
    counts = [row[1] for row in rows]
    
    return {"categories": categories, "counts": counts}

# Retrieve upload trends (number of uploads per day)
def get_upload_trends():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DATE(upload_time) as upload_date, COUNT(*) FROM documents GROUP BY upload_date ORDER BY upload_date")
    rows = cursor.fetchall()
    
    conn.close()

    upload_times = {row[0]: row[1] for row in rows}
    return upload_times

# Retrieve the distribution of confidence scores
def get_confidence_distribution():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT confidence FROM documents")
    rows = cursor.fetchall()
    
    conn.close()
    
    confidence_scores = [row[0] for row in rows]
    return confidence_scores

# Run database initialization
init_db()