import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import config

# Singleton Chroma Client
_client = chromadb.PersistentClient(
    path=config.CHROMA_PERSIST_DIR,
    settings=Settings(anonymized_telemetry=False)
)

embedder = GoogleGenerativeAIEmbeddings(
    model=config.EMBEDDING_MODEL,
    google_api_key=config.GOOGLE_API_KEY,
    task_type="retrieval_document"
)

query_embedder = GoogleGenerativeAIEmbeddings(
    model=config.EMBEDDING_MODEL,
    google_api_key=config.GOOGLE_API_KEY,
    task_type="retrieval_query"
)

def get_chroma_store(namespace: str, is_query: bool = False):
    """
    Returns a consistent Chroma instance for a given namespace.
    """
    return Chroma(
        client=_client,
        collection_name=namespace,
        embedding_function=query_embedder if is_query else embedder
    )
