from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import Document
from config import config

library_bp = Blueprint("library", __name__)

@library_bp.route("", methods=["GET"])
def get_library():
    try:
        namespace = request.args.get("namespace")
        
        with SessionLocal() as session:
            query = session.query(Document)
            if namespace:
                query = query.filter(Document.namespace == namespace)
            
            documents = query.all()
            
            result = []
            for doc in documents:
                result.append({
                    "id": doc.id,
                    "title": doc.title,
                    "doc_type": doc.doc_type,
                    "namespace": doc.namespace,
                    "chunk_count": doc.chunk_count,
                    "created_at": doc.created_at.isoformat()
                })
            
            return jsonify({"documents": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route("/<int:doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    try:
        with SessionLocal() as session:
            doc = session.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return jsonify({"error": "Document not found"}), 404
            
            # Try to delete from Chroma using its internal collection
            try:
                from services.chat_service import _get_collection
                vector_store = _get_collection(doc.namespace)
                
                # We attempt to delete based on source metadata, which matches either title, filename or url
                source_val = doc.source_url if doc.doc_type == "url" else doc.title
                
                # For PDFs, PyPDFLoader often uses the file path. Let's try multiple potential source names just in case
                if doc.doc_type == "pdf":
                    vector_store._collection.delete(where={"source": {"$contains": doc.title}})
                else:
                    vector_store._collection.delete(where={"source": source_val})
            except Exception as ce:
                print(f"Warning: Failed to delete from Chroma: {ce}")
            
            session.delete(doc)
            session.commit()
            
            return jsonify({"success": True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
