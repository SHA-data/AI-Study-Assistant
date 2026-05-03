import sqlite3

def check_db():
    try:
        conn = sqlite3.connect('study_assistant.db')
        cursor = conn.cursor()
        
        print("--- Documents ---")
        cursor.execute("SELECT id, title, namespace, doc_type FROM documents")
        docs = cursor.fetchall()
        for row in docs:
            print(row)
            
        print(f"\nTotal documents: {len(docs)}")
        
        print("\n--- Unique Namespaces ---")
        cursor.execute("SELECT DISTINCT namespace FROM documents")
        for row in cursor.fetchall():
            print(row)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
