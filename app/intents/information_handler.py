from app.intents.base_handler import BaseIntentHandler
from app.services.intent_service import detect_intent
from app.services.public_information_service import handle_information_request


class InformationHandler(BaseIntentHandler):
    """Dispatch public-information intents to their service functions."""

    def handle(self, user_id: int, message: str) -> str:
        intent, _, _ = detect_intent(message)
        return handle_information_request(intent, message)
