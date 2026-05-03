import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

os.environ["ANONYMIZED_TELEMETRY"] = "False"

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    CHROMA_PERSIST_DIR = os.path.abspath(os.getenv("CHROMA_PERSIST_DIR", "./chroma_store"))
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./study_assistant.db")
    
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5001))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    # Model Constants
    LLM_MODEL = "llama-3.3-70b-versatile"
    EMBEDDING_MODEL = "models/gemini-embedding-001"
    
    # Claim Statuses
    STATUS_ACTIVE = "active"
    STATUS_SUPPORTED = "supported"
    STATUS_UNVERIFIED = "unverified"
    
    # Document Types
    DOC_TYPE_PDF = "pdf"
    DOC_TYPE_TEXT = "text"
    DOC_TYPE_URL = "url"
    DOC_TYPE_PPTX = "pptx"

    # Namespaces
    NAMESPACE_SHARED = "shared"

config = Config()
