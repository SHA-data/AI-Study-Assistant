from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import Claim
from services import claim_service
from config import config

claims_bp = Blueprint("claims", __name__)

@claims_bp.route("", methods=["GET"])
def get_claims():
    try:
        member = request.args.get("member")
        status = request.args.get("status")
        conv_id = request.args.get("conv_id")
        
        with SessionLocal() as session:
            query = session.query(Claim)
            if member:
                query = query.filter(Claim.claimant == member)
            if status:
                query = query.filter(Claim.status == status)
            if conv_id:
                query = query.filter(Claim.conversation_id == conv_id)
            
            claims = query.order_by(Claim.timestamp.desc()).all()
            
            result = []
            for c in claims:
                result.append({
                    "id": c.id,
                    "claimant": c.claimant,
                    "claim_text": c.claim_text,
                    "conversation_id": c.conversation_id,
                    "timestamp": c.timestamp.isoformat(),
                    "status": c.status,
                    "evidence": c.evidence
                })
            
            return jsonify({"claims": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@claims_bp.route("/<int:claim_id>", methods=["GET"])
def get_claim(claim_id):
    try:
        with SessionLocal() as session:
            claim = session.query(Claim).filter(Claim.id == claim_id).first()
            if not claim:
                return jsonify({"error": "Claim not found"}), 404
            
            return jsonify({
                "id": claim.id,
                "claimant": claim.claimant,
                "claim_text": claim.claim_text,
                "conversation_id": claim.conversation_id,
                "timestamp": claim.timestamp.isoformat(),
                "status": claim.status,
                "evidence": claim.evidence
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@claims_bp.route("/check", methods=["POST"])
def check_claims():
    try:
        result = claim_service.re_evaluate_all()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
