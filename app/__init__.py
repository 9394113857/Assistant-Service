import os
import json
import html
import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, jsonify, request
from .config import Config
from .extensions import db, migrate, jwt
from flask_cors import CORS

# ✅ IMPORTANT: Import models so Alembic detects them
from .models.chat_session import ChatSession
from .models.chat_message import ChatMessage
from .models.assistant_training_log import AssistantTrainingLog


def create_app(testing: bool = False):
    app = Flask(__name__)

    # --------------------------
    # Base Config
    # --------------------------
    app.config.from_object(Config)

    # 🔥 DEBUG PRINT (CRITICAL)
    # print("🔥 ACTIVE DATABASE:", app.config["SQLALCHEMY_DATABASE_URI"])

    if testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SECRET_KEY"] = "test-secret"
        app.config["JWT_SECRET_KEY"] = "test-jwt-secret"

    # --------------------------
    # Extensions
    # --------------------------
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # --------------------------
    # 🔥 Load ML Model at Startup
    # --------------------------
    from .services.ml_model_loader import load_model
    load_model()

    # --------------------------
    # Logging Setup
    # --------------------------
    logs_path = os.path.join(os.getcwd(), "logs")
    os.makedirs(logs_path, exist_ok=True)

    log_file = os.path.join(logs_path, "assistant.log")

    handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )

    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    ))

    if not app.logger.handlers:
        app.logger.addHandler(handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Assistant service starting...")

    # --------------------------
    # Log Every Request
    # --------------------------
    @app.before_request
    def log_request():
        app.logger.info(
            f"Incoming {request.method} {request.path}"
        )

    @app.after_request
    def log_response(response):
        app.logger.info(
            f"Response {response.status}"
        )
        return response

    # --------------------------
    # Register Routes
    # --------------------------
    from .routes.assistant_routes import assistant_bp
    app.register_blueprint(assistant_bp, url_prefix="/api/v1/assistant")

    # --------------------------
    # Build metadata and Health Check
    # --------------------------
    def get_build_info():
        metadata_path = os.path.join(os.getcwd(), "build_info.json")
        try:
            with open(metadata_path, encoding="utf-8") as metadata_file:
                return json.load(metadata_file)
        except (OSError, json.JSONDecodeError):
            return {
                "version": os.getenv("APP_VERSION", "unknown"),
                "commit": os.getenv("APP_COMMIT", "unknown"),
                "branch": os.getenv("APP_BRANCH", "unknown"),
                "build_time_utc": os.getenv("BUILD_TIME_UTC", "unknown"),
                "build_time_ist": os.getenv("BUILD_TIME_IST", "unknown"),
            }

    @app.get("/")
    def health():
        info = get_build_info()
        payload = {"status": "UP", "service": "Assistant Service", "build": info}
        if "text/html" in request.headers.get("Accept", ""):
            return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Assistant Service</title><style>
body {{font-family:Arial,sans-serif;background:#0f172a;color:#e2e8f0;text-align:center;padding:48px 16px}}
main {{display:inline-block;text-align:left;background:#1e293b;padding:28px 36px;border-radius:12px;max-width:720px}}
h1 {{color:#38bdf8}} .up {{color:#22c55e;font-weight:bold}} .label {{color:#94a3b8}} code {{overflow-wrap:anywhere}}
</style></head><body><main><h1>🚀 Assistant Service</h1><p class="up">🟢 UP</p>
<p><span class="label">Version:</span> {html.escape(str(info.get("version", "unknown")))}</p>
<p><span class="label">Commit:</span> <code>{html.escape(str(info.get("commit", "unknown")))}</code></p>
<p><span class="label">Branch:</span> {html.escape(str(info.get("branch", "unknown")))}</p>
<p><span class="label">UTC:</span> {html.escape(str(info.get("build_time_utc", "unknown")))}</p>
<p><span class="label">IST:</span> {html.escape(str(info.get("build_time_ist", "unknown")))}</p>
</main></body></html>'''
        return jsonify(payload), 200

    app.logger.info("Assistant service started successfully.")
    return app


# Flow:-
# create_app()
#      ↓
# load_model()
#      ↓
# If model file exists → load into memory
# If not → fallback to rule-based
