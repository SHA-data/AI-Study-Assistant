import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from services import ingest_service
from config import config

ingest_bp = Blueprint("ingest", __name__)

@ingest_bp.route("/pdf", methods=["POST"])
def ingest_pdf():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files["file"]
        namespace = request.form.get("namespace")
        title = request.form.get("title")

        if not file or not namespace:
            return jsonify({"error": "Missing file or namespace"}), 400
        
        if not file.filename.endswith(".pdf"):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(config.UPLOAD_DIR, filename)
        file.save(file_path)

        db_doc = ingest_service.ingest_pdf(file_path, namespace, title)
        
        return jsonify({
            "doc_id": db_doc.id,
            "title": db_doc.title,
            "chunk_count": db_doc.chunk_count,
            "namespace": db_doc.namespace
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ingest_bp.route("/pptx", methods=["POST"])
def ingest_pptx():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files["file"]
        namespace = request.form.get("namespace")
        title = request.form.get("title")

        if not file or not namespace:
            return jsonify({"error": "Missing file or namespace"}), 400
        
        if not file.filename.endswith(".pptx"):
            return jsonify({"error": "Only PPTX files are allowed"}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(config.UPLOAD_DIR, filename)
        file.save(file_path)

        db_doc = ingest_service.ingest_pptx(file_path, namespace, title)
        
        return jsonify({
            "doc_id": db_doc.id,
            "title": db_doc.title,
            "chunk_count": db_doc.chunk_count,
            "namespace": db_doc.namespace
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@ingest_bp.route("/text", methods=["POST"])
def ingest_text():
    try:
        data = request.get_json()
        text = data.get("text")
        namespace = data.get("namespace")
        title = data.get("title")

        if not text or not namespace or not title:
            return jsonify({"error": "Missing text, namespace, or title"}), 400

        db_doc = ingest_service.ingest_text(text, namespace, title)
        
        return jsonify({
            "doc_id": db_doc.id,
            "title": db_doc.title,
            "chunk_count": db_doc.chunk_count,
            "namespace": db_doc.namespace
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@ingest_bp.route("/url", methods=["POST"])
def ingest_url():
    try:
        data = request.get_json()
        url = data.get("url")
        namespace = data.get("namespace")
        title = data.get("title")

        if not url or not namespace or not title:
            return jsonify({"error": "Missing url, namespace, or title"}), 400

        db_doc = ingest_service.ingest_url(url, namespace, title)
        
        return jsonify({
            "doc_id": db_doc.id,
            "title": db_doc.title,
            "chunk_count": db_doc.chunk_count,
            "namespace": db_doc.namespace,
            "source_url": db_doc.source_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
