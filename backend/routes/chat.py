from flask import Blueprint, request, jsonify
from services import chat_service

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message")
        namespace = data.get("namespace")
        member_name = data.get("member_name")
        conversation_id = data.get("conversation_id")

        subject = data.get("subject", "General")
        
        if not message or not namespace or not member_name or not conversation_id:
            return jsonify({"error": "Missing required fields"}), 400

        result = chat_service.chat(message, namespace, member_name, conversation_id, subject)
        
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
