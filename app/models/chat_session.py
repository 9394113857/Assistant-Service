from datetime import datetime
from app.extensions import db


class ChatSession(db.Model):
    __tablename__ = "chat_sessions"
    __table_args__ = (
        db.UniqueConstraint(
            "guest_token_hash",
            name="uq_chat_sessions_guest_token_hash",
        ),
    )

    # Primary key for each chat session
    id = db.Column(db.Integer, primary_key=True)

    # User ID can be NULL for guest users
    # Logged-in users will have a real user_id
    user_id = db.Column(db.Integer, nullable=True)

    # Store only a SHA-256 digest of the opaque guest token.
    # Existing guest sessions remain NULL and are never reused by new guests.
    guest_token_hash = db.Column(db.String(64), nullable=True)

    # Timestamp when session was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with chat messages
    messages = db.relationship(
        "ChatMessage",
        backref="session",
        lazy=True
    )

# flask db migrate -m "add isolated guest chat sessions"
# flask db upgrade
