from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    doc_type = Column(String, nullable=False)  # "pdf" | "text" | "url"
    namespace = Column(String, nullable=False)  # "shared" or member name
    chunk_count = Column(Integer)
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claimant = Column(String, nullable=False)
    claim_text = Column(Text, nullable=False)
    conversation_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    status = Column(String, default="active")  # "active" | "supported" | "contradicted"
    evidence = Column(JSON, nullable=True)  # list of {title, source, relevance_snippet}
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
