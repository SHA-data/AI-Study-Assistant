import chromadb
from chromadb.config import Settings
import os

def check_chroma():
    persist_dir = "./chroma_store"
    if not os.path.exists(persist_dir):
        print(f"Error: Persist directory {persist_dir} does not exist.")
        return

    client = chromadb.PersistentClient(path=persist_dir, settings=Settings(anonymized_telemetry=False))
    
    print("--- ChromaDB Collections ---")
    collections = client.list_collections()
    if not collections:
        print("No collections found.")
    else:
        for coll in collections:
            count = coll.count()
            print(f"Collection: {coll.name} | Documents: {count}")
            
if __name__ == "__main__":
    check_chroma()
