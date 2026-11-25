from datetime import datetime
from functools import wraps

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from app.extensions import db
from app.models.assistant_training_log import AssistantTrainingLog
from app.services.assistant_orchestrator import (
    GuestSessionNotFound,
    process_user_message,
)
from app.services.intent_registry import INTENT_HANDLER_MAP

assistant_bp = Blueprint("assistant", __name__)


def admin_required(view):
    """Require a valid Auth-Service access token carrying role=admin."""
    @wraps(view)
    @jwt_required()
    def wrapped(*args, **kwargs):
        if get_jwt().get("role") != "admin":
            return jsonify({"error": "Administrator access required"}), 403
        try:
            reviewer_id = int(get_jwt_identity())
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid reviewer identity"}), 403
        return view(reviewer_id=reviewer_id, *args, **kwargs)
    return wrapped


@assistant_bp.post("/chat")
@jwt_required(optional=True)
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message is required"}), 400

    # Never trust a user_id supplied in the request body. Authenticated identity
    # must come from the verified Auth-Service JWT; no token means guest chat.
    token_identity = get_jwt_identity()
    if token_identity is None:
        user_id = None
        guest_session_token = data.get("guest_session_token")
        if guest_session_token is not None and (
            not isinstance(guest_session_token, str)
            or not guest_session_token.strip()
            or len(guest_session_token) > 256
        ):
            return jsonify({"error": "Invalid guest_session_token"}), 400
    else:
        try:
            user_id = int(token_identity)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid authenticated user identity"}), 401
        # A guest token must never select or influence an authenticated session.
        guest_session_token = None

    try:
        result = process_user_message(
            user_id,
            message,
            guest_session_token=guest_session_token,
        )
    except GuestSessionNotFound:
        return jsonify({"error": "Guest session not found. Start a new chat."}), 401

    return jsonify(result)


@assistant_bp.get("/training/review-queue")
@admin_required
def training_review_queue(reviewer_id):
    """List training examples for an authenticated administrator to review."""
    status = request.args.get("status", "pending").strip().lower()
    if status not in {"pending", "reviewed", "all"}:
        return jsonify({"error": "status must be pending, reviewed, or all"}), 400

    try:
        limit = min(max(int(request.args.get("limit", 50)), 1), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
    except (TypeError, ValueError):
        return jsonify({"error": "limit and offset must be integers"}), 400

    query = AssistantTrainingLog.query
    if status == "pending":
        query = query.filter(AssistantTrainingLog.actual_intent.is_(None))
    elif status == "reviewed":
        query = query.filter(AssistantTrainingLog.actual_intent.is_not(None))

    total = query.count()
    records = (
        query.order_by(AssistantTrainingLog.created_at.asc(), AssistantTrainingLog.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return jsonify({
        "items": [{
            "id": item.id,
            "user_message": item.user_message,
            "predicted_intent": item.predicted_intent,
            "confidence_score": item.confidence_score,
            "actual_intent": item.actual_intent,
            "model_version": item.model_version,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "reviewer_user_id": item.reviewer_user_id,
            "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
        } for item in records],
        "total": total,
        "limit": limit,
        "offset": offset,
        "status": status,
    }), 200


@assistant_bp.post("/training/<int:record_id>/review")
@admin_required
def review_training_record(reviewer_id, record_id):
    """Set a human-verified intent exactly once and retain reviewer audit metadata."""
    data = request.get_json(silent=True) or {}
    actual_intent = data.get("actual_intent")

    if not isinstance(actual_intent, str):
        return jsonify({"error": "actual_intent is required"}), 400

    actual_intent = actual_intent.strip().lower()
    if actual_intent not in INTENT_HANDLER_MAP:
        return jsonify({
            "error": "Unsupported intent",
            "allowed_intents": sorted(INTENT_HANDLER_MAP.keys()),
        }), 400

    record = db.session.get(AssistantTrainingLog, record_id)
    if record is None:
        return jsonify({"error": "Training record not found"}), 404

    reviewed_at = datetime.utcnow()
    updated = (
        AssistantTrainingLog.query
        .filter_by(id=record_id, actual_intent=None)
        .update({
            AssistantTrainingLog.actual_intent: actual_intent,
            AssistantTrainingLog.reviewer_user_id: reviewer_id,
            AssistantTrainingLog.reviewed_at: reviewed_at,
        }, synchronize_session=False)
    )

    if updated != 1:
        db.session.rollback()
        return jsonify({"error": "Training record has already been reviewed"}), 409

    db.session.commit()
    return jsonify({
        "message": "Training record reviewed successfully",
        "id": record_id,
        "actual_intent": actual_intent,
        "reviewer_user_id": reviewer_id,
        "reviewed_at": reviewed_at.isoformat(),
    }), 200
