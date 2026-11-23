"""Regression tests keeping rule-based intents aligned with handler registration."""

import unittest

from app.services.intent_registry import INTENT_HANDLER_MAP
from app.services.intent_service import detect_intent


class IntentRegistryAlignmentTests(unittest.TestCase):
    def test_every_representative_detected_intent_has_a_registered_handler(self):
        messages = {
            "hello bro": "greeting",
            "who are you": "assistant_identity",
            "what can you help me with": "assistant_about",
            "Can you explain that in simpler words?": "clarification",
            "show products": "show_products",
            "show laptops": "product_category",
            "show me cheaper products": "cheaper_product",
            "what is your costliest product": "costliest_product",
            "show me the details of this laptop": "product_detail",
            "what is the price of this product": "product_price",
            "which products are available in stock": "product_stock",
            "compare these two products": "product_compare",
            "show alternatives": "product_alternatives",
            "help me choose a suitable product": "product_advice",
            "add this product to my cart": "add_to_cart",
            "show my cart": "view_cart",
            "show my orders": "show_orders",
            "track my order": "track_order",
            "recommend products for me": "recommend_product",
            "weather in Hyderabad": "weather",
            "wiki Python": "wikipedia",
            "movie Interstellar": "movie",
            "book Atomic Habits": "book",
            "synonym happy": "synonym",
            "meaning resilience": "meaning",
            "latest news": "news",
            "tell me a joke": "joke",
            "share a random fact": "random_fact",
            "give me a quote": "quote",
            "corona stats": "covid_stats",
            "what is the capital of Japan": "general_knowledge",
            "asdfghjkl": "unknown",
        }

        for message, expected_intent in messages.items():
            with self.subTest(message=message):
                detected_intent, _, _ = detect_intent(message)
                self.assertEqual(detected_intent, expected_intent)
                self.assertIn(
                    detected_intent,
                    INTENT_HANDLER_MAP,
                    msg=f"Detected intent '{detected_intent}' has no registered handler",
                )

    def test_unknown_intent_has_a_registered_fallback_handler(self):
        self.assertIn("unknown", INTENT_HANDLER_MAP)


if __name__ == "__main__":
    unittest.main()
