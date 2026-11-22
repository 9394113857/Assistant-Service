import re

from app.intents.base_handler import BaseIntentHandler
from app.services.intent_service import detect_intent
from app.services.tool_router import handle_product_request


class ProductHandler(BaseIntentHandler):

    def handle(self, user_id: int, message: str) -> str:
        intent, _, _ = detect_intent(message)

        if intent == "product_stock":
            return (
                "I can show the product catalogue, but the current catalogue "
                "integration does not provide a verified stock quantity or "
                "availability field. I can't confirm stock yet."
            )

        if intent == "product_compare":
            return (
                "Product comparison is not available in chat yet. "
                "Please share the exact product names you want to compare."
            )

        if intent == "product_alternatives":
            return (
                "I can't identify alternatives from the current chat catalogue yet. "
                "Please share the product name or category you are interested in."
            )

        if intent == "product_advice":
            return (
                "I'd be happy to help you choose. Which product category are you "
                "looking for, and what is your approximate budget?"
            )

        if intent in {"product_detail", "product_price"}:
            # A product name should be present after follow-up resolution.
            generic_reference = re.search(
                r"\b(this|that|first|second|third|it)\s+(?:product|item|one)\b",
                message.lower(),
            )
            if generic_reference or not re.search(
                r"\b(laptop|phone|mobile|smartphone|tablet|camera|tv|monitor|printer|"
                r"headphone|earbud|gaming|item-\d+)\b",
                message.lower(),
            ):
                return "Which product would you like details or pricing for? Please mention its name."

        try:
            response = handle_product_request(message=message)
            if not response:
                return "Sorry, I couldn't find any products right now."
            return response
        except Exception:
            return "Product service is temporarily unavailable. Please try again later."
