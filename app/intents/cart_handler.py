from app.intents.base_handler import BaseIntentHandler


class CartHandler(BaseIntentHandler):
    """Return an explicit capability message until cart API actions are integrated."""

    def handle(self, user_id: int, message: str) -> str:
        return (
            "Cart actions are not connected to the chat assistant yet. "
            "You can browse products here, but please use the storefront cart "
            "to add items or review your cart."
        )
