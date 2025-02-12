import sqlite3

DATABASE_PATH = "documents.db"

def fetch_all_documents():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM documents")
        rows = cursor.fetchall()
        
        if not rows:
            print("No data found.")
        
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

fetch_all_documents()
