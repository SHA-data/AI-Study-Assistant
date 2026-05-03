import json
from typing import List, Dict
from langchain_groq import ChatGroq
from config import config
from database import SessionLocal
from models import Claim, Document as DBDocument
from services.vector_store import get_chroma_store
import os

# Initialize components
llm = ChatGroq(
    model=config.LLM_MODEL,
    groq_api_key=config.GROQ_API_KEY,
    temperature=0
)

def _get_all_collections() -> List[str]:
    """
    Returns all existing collection names in ChromaDB.
    """
    with SessionLocal() as session:
        namespaces = session.query(DBDocument.namespace).distinct().all()
        results = [ns[0] for ns in namespaces]
        if config.NAMESPACE_SHARED not in results:
            results.append(config.NAMESPACE_SHARED)
        return results

def _ground_claim(claim_text: str, namespace: str = None) -> List[Dict]:
    """
    Retrieves k=6 most relevant chunks. 
    Searches primary namespace + shared, with a fallback to all collections if nothing found.
    """
    if namespace:
        namespaces = [namespace]
        if namespace != config.NAMESPACE_SHARED:
            namespaces.append(config.NAMESPACE_SHARED)
    else:
        namespaces = _get_all_collections()
        
    all_evidence = []
    print(f"DEBUG: Grounding claim: {claim_text} | Namespaces: {namespaces}")
    
    for ns in namespaces:
        try:
            store = get_chroma_store(ns, is_query=True)
            docs = store.similarity_search(claim_text, k=4)
            for doc in docs:
                all_evidence.append({
                    "title": doc.metadata.get("source", os.path.basename(doc.metadata.get("source", "Unknown"))),
                    "source": ns,
                    "relevance_snippet": doc.page_content[:300] + "..."
                })
        except Exception as e:
            print(f"Warning: Failed to search in namespace {ns}: {e}")
            continue
    
    # Fallback: if no evidence found in specific namespaces, try EVERYTHING
    if not all_evidence and namespace:
        print("DEBUG: No evidence in primary namespaces, trying global fallback...")
        all_ns = _get_all_collections()
        for ns in all_ns:
            if ns in namespaces: continue # Already checked
            try:
                store = get_chroma_store(ns, is_query=True)
                docs = store.similarity_search(claim_text, k=2)
                for doc in docs:
                    all_evidence.append({
                        "title": doc.metadata.get("source", "Unknown"),
                        "source": ns,
                        "relevance_snippet": doc.page_content[:300] + "..."
                    })
            except: continue

    # Sort and limit
    return all_evidence[:6]

def extract_and_store(user_message: str, assistant_answer: str, member_name: str, conversation_id: str, namespace: str = None) -> List[Claim]:
    """
    Extracts claims from assistant response and grounds them in the knowledge base.
    """
    try:
        # Prompt for extraction
        prompt = f"""
        You are an expert academic auditor. Analyze the following Assistant response and extract a list of discrete factual claims.
        
        Assistant Response: "{assistant_answer}"
        
        Rules:
        1. Extract ONLY specific, verifiable statements.
        2. Format the output as a JSON list of strings: ["claim 1", "claim 2"]
        3. If no claims, return [].
        """
        
        response = llm.invoke(prompt)
        json_str = response.content.strip()
        
        # Clean potential markdown
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
            
        try:
            claims_data = json.loads(json_str)
        except:
            start, end = json_str.find("["), json_str.rfind("]")
            claims_data = json.loads(json_str[start:end+1]) if start != -1 and end != -1 else []
                
        created_claims = []
        for claim_text in claims_data:
            with SessionLocal() as session:
                exists = session.query(Claim).filter(
                    Claim.conversation_id == conversation_id,
                    Claim.claim_text == claim_text
                ).first()
                if exists: continue
            
            evidence = _ground_claim(claim_text, namespace)
            
            new_claim = Claim(
                claimant="Assistant",
                claim_text=claim_text,
                conversation_id=conversation_id,
                status=config.STATUS_ACTIVE,
                evidence=evidence
            )
            
            with SessionLocal() as session:
                session.add(new_claim)
                session.commit()
                session.refresh(new_claim)
                created_claims.append(new_claim)
        return created_claims
    except Exception as e:
        print(f"Error extracting claims: {e}")
        return []

def re_evaluate_all() -> Dict:
    """
    Re-evaluates 'active' and 'unverified' claims against current knowledge base.
    """
    checked = 0
    updated = 0
    
    with SessionLocal() as session:
        # Check both active and previously unverified claims
        target_claims = session.query(Claim).filter(
            Claim.status.in_([config.STATUS_ACTIVE, config.STATUS_UNVERIFIED])
        ).all()
        
        for claim in target_claims:
            checked += 1
            evidence = _ground_claim(claim.claim_text)
            
            if not evidence:
                claim.status = config.STATUS_UNVERIFIED
                session.commit()
                continue

            evidence_text = "\n".join([e['relevance_snippet'] for e in evidence])
            
            prompt = f"""
            You are a factual claim auditor. 
            Does the following evidence support this claim?
            
            Claim: {claim.claim_text}
            Evidence: {evidence_text}
            
            Rules:
            - If confirmed, reply: supported
            - If not found or contradicted, reply: unverified
            
            Answer ONLY with: supported / unverified
            """
            
            response = llm.invoke(prompt)
            verdict = response.content.strip().lower()
            
            claim.evidence = evidence
            if "supported" in verdict:
                claim.status = config.STATUS_SUPPORTED
                updated += 1
            else:
                claim.status = config.STATUS_UNVERIFIED
            
            session.commit()
            
    return {"checked": checked, "updated": updated}
