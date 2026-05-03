from database import SessionLocal
from models import Document, Claim
import chromadb
from chromadb.config import Settings
import os

def diagnose():
    # 1. Check SQLite
    print("--- SQLite Documents ---")
    with SessionLocal() as session:
        docs = session.query(Document).all()
        for d in docs:
            print(f"ID: {d.id} | Title: {d.title} | Namespace: {d.namespace}")
            
    # 2. Check Chroma
    persist_dir = os.path.abspath("./chroma_store")
    print(f"\n--- ChromaDB (at {persist_dir}) ---")
    if not os.path.exists(persist_dir):
        print("Error: Persist directory not found!")
        return
        
    client = chromadb.PersistentClient(path=persist_dir, settings=Settings(anonymized_telemetry=False))
    collections = client.list_collections()
    for coll in collections:
        print(f"Collection: {coll.name} | Count: {coll.count()}")
        # Peak at one item
        if coll.count() > 0:
            peek = coll.peek(1)
            print(f"  Sample metadata: {peek['metadatas'][0]}")

if __name__ == "__main__":
    diagnose()
