from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from services.vector_store import get_chroma_store
from config import config

# Initialize components once
llm = ChatGroq(
    model=config.LLM_MODEL,
    groq_api_key=config.GROQ_API_KEY,
    temperature=0
)

embedder = GoogleGenerativeAIEmbeddings(
    model=config.EMBEDDING_MODEL,
    google_api_key=config.GOOGLE_API_KEY
)

SYSTEM_PROMPT = """
You are a helpful and concise study assistant. The user is a student studying the subject: "{subject}".

Available Documents in your Knowledge Base:
{library_summary}

Retrieved Context (excerpts from the Knowledge Base):
{context}

Instructions:
1. **Conciseness is Key**: Provide minimal, to-the-point answers. Avoid long paragraphs. Explain with examples if possible.
2. **Structure**: Use Markdown for structure. Use **bolding** for key terms and bulleted lists for explaining multiple points.
3. **Student-Friendly**: Explain concepts in simple, easy-to-understand words as if explaining to a peer.
4. **Factual Accuracy**: Use the Retrieved Context to answer specific questions. Cite the source document (e.g., Source: filename.pdf).
5. **Conversational**: For greetings, respond naturally and briefly.
6. **Library Awareness**: If the user asks what topics or materials are available, do NOT simply list the filenames (e.g., "6.pptx"). Instead, use the **Retrieved Context** to identify the actual academic topics and subject matter covered within those documents and present them as a structured, bulleted list of topics.
7. **No Hallucination**: If the Retrieved Context doesn't contain the answer, say so clearly, then briefly offer a general explanation from your own knowledge.
8. **No Abusive Language: If any abusive language is used from user, dont answer at all and give a one line warning to not to it again.**
Question:
{question}
"""

def _build_chain(context_text: str, library_summary: str, subject: str):
    """
    Builds the LCEL chain.
    """
    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
    return (
        {
            "context": lambda x: context_text, 
            "library_summary": lambda x: library_summary,
            "subject": lambda x: subject,
            "question": RunnablePassthrough()
        } | prompt | llm | StrOutputParser()
    )

def chat(message: str, namespace: str, member_name: str, conversation_id: str, subject: str = "General") -> Dict:
    """
    RAG retrieval and response generation.
    """
    # Search multiple namespaces: the provided one and the 'shared' library
    search_namespaces = [namespace]
    if namespace != config.NAMESPACE_SHARED:
        search_namespaces.append(config.NAMESPACE_SHARED)
    
    context_docs = []
    for ns in search_namespaces:
        try:
            store = get_chroma_store(ns, is_query=True)
            docs = store.similarity_search(message, k=4)
            context_docs.extend(docs)
        except Exception as e:
            print(f"Warning: Failed to retrieve from namespace {ns}: {e}")
    
    # Deduplicate and limit total context docs
    # Simple deduplication based on page content
    seen = set()
    unique_docs = []
    for doc in context_docs:
        if doc.page_content not in seen:
            unique_docs.append(doc)
            seen.add(doc.page_content)
    
    context_docs = unique_docs[:8]
    
    context_text = "\n\n".join([doc.page_content for doc in context_docs])
    print("\nRETRIEVED CONTEXT")
    print(context_text)
    print("\n\n")
    
    # Fetch library summary from DB to give the AI meta-awareness of uploaded files
    library_summary = "No documents found."
    try:
        from database import SessionLocal
        from models import Document
        with SessionLocal() as session:
            docs = session.query(Document).filter(Document.namespace == namespace).all()
            if docs:
                library_summary = "\n".join([f"- {doc.title} ({doc.doc_type})" for doc in docs])
    except Exception as e:
        print(f"Warning: Failed to fetch library summary: {e}")
    
    chain = _build_chain(context_text, library_summary, subject)
    answer = chain.invoke(message)
    
    sources = []
    for doc in context_docs:
        sources.append({
            "title": doc.metadata.get("source", "Unknown"),
            "namespace": namespace,
            "chunk": doc.page_content[:200] + "..."
        })

    # Trigger claim extraction
    try:
        from services import claim_service
        claim_service.extract_and_store(message, answer, member_name, conversation_id, namespace)
    except Exception as e:
        print(f"Claim extraction failed: {e}")

    return {
        "answer": answer,
        "sources": sources,
        "conversation_id": conversation_id
    }
