import os

import joblib

from app.services.ml_intent_scope import model_matches_initial_scope

MODEL_PATH = os.path.join(
    os.getcwd(),
    "models",
    "assistant_intent_model.pkl",
)

model = None
model_version = "ml_five_intent_v1"


def load_model():
    """Load only a validated five-intent artifact; fail safely to rule-based routing."""
    global model
    model = None

    if not os.path.exists(MODEL_PATH):
        print("⚠ ML model not found. Falling back to rule-based intent detection.")
        return None

    try:
        candidate = joblib.load(MODEL_PATH)
        if not model_matches_initial_scope(candidate):
            print(
                "⚠ ML model rejected: its classes do not exactly match the "
                "approved five-intent scope. Falling back to rule-based detection."
            )
            return None

        model = candidate
        print("✅ Validated five-intent ML model loaded successfully.")
        return model
    except Exception as exc:
        print(
            "⚠ ML model could not be loaded "
            f"({type(exc).__name__}). Falling back to rule-based detection."
        )
        return None


def get_model():
    return model, model_version
