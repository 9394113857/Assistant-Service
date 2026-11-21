from app.intents.product_handler import ProductHandler
from app.intents.order_handler import OrderHandler
from app.intents.recommendation_handler import RecommendationHandler
from app.intents.greeting_handler import GreetingHandler
from app.intents.information_handler import InformationHandler
from app.intents.unknown_handler import UnknownHandler


INTENT_HANDLER_MAP = {
    # Existing commerce capabilities
    "product": ProductHandler,
    "show_products": ProductHandler,
    "cheaper_product": ProductHandler,
    "product_category": ProductHandler,
    "order": OrderHandler,
    "show_orders": OrderHandler,
    "track_order": OrderHandler,
    "recommendation": RecommendationHandler,
    "recommend_product": RecommendationHandler,

    # Conversation and assistant information
    "greeting": GreetingHandler,
    "assistant_identity": GreetingHandler,
    "assistant_about": GreetingHandler,

    # Public information capabilities
    "weather": InformationHandler,
    "wikipedia": InformationHandler,
    "movie": InformationHandler,
    "book": InformationHandler,
    "synonym": InformationHandler,
    "meaning": InformationHandler,
    "news": InformationHandler,
    "joke": InformationHandler,
    "random_fact": InformationHandler,
    "quote": InformationHandler,
    "covid_stats": InformationHandler,
    "general_knowledge": InformationHandler,

    "unknown": UnknownHandler,
}


def get_intent_handler(intent):
    handler_class = INTENT_HANDLER_MAP.get(intent, UnknownHandler)
    return handler_class()
