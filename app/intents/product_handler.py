from app.intents.base_handler import BaseIntentHandler
from app.services.tool_router import handle_product_request


class ProductHandler(BaseIntentHandler):

    def handle(self, user_id: int, message: str) -> str:
        try:
            response = handle_product_request(message=message)

            if not response:
                return "Sorry, I couldn't find any products right now."

            return response

        except Exception as e:
            print("Product handler error:", e)
            return "Product service is temporarily unavailable. Please try again later."
