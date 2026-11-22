from datetime import datetime
from app.extensions import db


class AssistantTrainingLog(db.Model):
    __tablename__ = "assistant_training_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    user_message = db.Column(db.Text, nullable=False)
    predicted_intent = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    actual_intent = db.Column(db.String(100), nullable=True)
    model_version = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Audit fields set only by an authenticated administrator review.
    reviewer_user_id = db.Column(db.Integer, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
