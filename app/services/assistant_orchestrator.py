from app.extensions import db
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.assistant_training_log import AssistantTrainingLog

from app.services.intent_service import detect_intent
from app.services.intent_registry import get_intent_handler
from app.services.followup_resolver import resolve_followup

CONFIDENCE_THRESHOLD = 0.60

# Keep these names aligned with intent_service.py and intent_registry.py.
LOGIN_REQUIRED_INTENTS = {
    "order", "show_orders", "track_order",
    "recommendation", "recommend_product",
}


def process_user_message(user_id, message):
    message = (message or "").strip()
    if not message:
        return {
            "response": "Please enter a message.",
            "intent": "unknown",
            "confidence": 0.0,
            "model_version": "rule_v2",
        }

    # Session management
    session = (
        ChatSession.query
        .filter_by(user_id=user_id)
        .order_by(ChatSession.created_at.desc())
        .first()
    )

    if not session:
        session = ChatSession(user_id=user_id)
        db.session.add(session)
        db.session.commit()

    # Load recent conversation context
    recent_messages = (
        ChatMessage.query
        .filter_by(session_id=session.id)
        .order_by(ChatMessage.id.desc())
        .limit(3)
        .all()
    )
    conversation_context = [
        f"{item.role}: {item.message}"
        for item in reversed(recent_messages)
    ]

    db.session.add(ChatMessage(
        session_id=session.id,
        role="user",
        message=message,
    ))
    db.session.commit()

    resolved_message = resolve_followup(message, conversation_context)
    intent, confidence_score, model_version = detect_intent(resolved_message)

    if confidence_score is None or confidence_score < CONFIDENCE_THRESHOLD:
        intent = "unknown"

    # Only commerce actions that access account-specific data require login.
    if user_id is None and intent in LOGIN_REQUIRED_INTENTS:
        assistant_reply = (
            "Please login to access your orders and personalized recommendations."
        )
    else:
        handler = get_intent_handler(intent)
        assistant_reply = handler.handle(user_id=user_id, message=resolved_message)

    db.session.add(ChatMessage(
        session_id=session.id,
        role="assistant",
        message=assistant_reply,
    ))
    db.session.add(AssistantTrainingLog(
        user_id=user_id,
        user_message=message,
        predicted_intent=intent,
        confidence_score=confidence_score,
        model_version=model_version,
    ))
    db.session.commit()

    return {
        "response": assistant_reply,
        "intent": intent,
        "confidence": confidence_score,
        "model_version": model_version,
    }
