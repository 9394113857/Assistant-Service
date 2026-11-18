import unittest

from app.services.intent_service import detect_intent


class IntentServiceTests(unittest.TestCase):
    def test_reference_bot_commands_are_recognized(self):
        cases = {
            "good morning": "greeting",
            "who are you": "assistant_identity",
            "about": "assistant_about",
            "weather in Hyderabad": "weather",
            "wiki Python": "wikipedia",
            "movie Interstellar": "movie",
            "book Atomic Habits": "book",
            "synonym happy": "synonym",
            "meaning resilience": "meaning",
            "news": "news",
            "joke": "joke",
            "fact": "random_fact",
            "quote": "quote",
            "coronastats": "covid_stats",
        }
        for message, expected in cases.items():
            with self.subTest(message=message):
                intent, confidence, version = detect_intent(message)
                self.assertEqual(intent, expected)
                self.assertGreaterEqual(confidence, 0.60)
                self.assertEqual(version, "rule_v2")

    def test_existing_ecommerce_intents_are_recognized(self):
        cases = {
            "show products": "show_products",
            "cheaper products": "cheaper_product",
            "show laptops": "product_category",
            "show my orders": "show_orders",
            "track my order": "track_order",
            "recommend a phone": "recommend_product",
        }
        for message, expected in cases.items():
            with self.subTest(message=message):
                self.assertEqual(detect_intent(message)[0], expected)

    def test_hi_is_not_matched_inside_another_word(self):
        self.assertEqual(detect_intent("which laptop is best")[0], "product_category")

    def test_empty_and_unknown_messages(self):
        self.assertEqual(detect_intent("")[0], "unknown")
        self.assertEqual(detect_intent("something unrelated")[0], "unknown")


if __name__ == "__main__":
    unittest.main()
