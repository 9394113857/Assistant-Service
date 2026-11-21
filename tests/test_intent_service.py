import unittest
import requests
from unittest.mock import patch

from app.services.assistant_orchestrator import LOGIN_REQUIRED_INTENTS
from app.services.intent_service import detect_intent
from app.services.public_information_service import get_general_knowledge
from app.services.followup_resolver import resolve_followup
from app.services.public_information_service import _query_after_command


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
                self.assertEqual(version, "rule_v3")

    def test_ecommerce_intents_keep_public_search_separate_from_private_actions(self):
        cases = {
            "show products": "show_products",
            "cheaper products": "cheaper_product",
            "what is your cheapest product": "cheaper_product",
            "find products below ₹20,000": "cheaper_product",
            "show laptops": "product_category",
            "do you have any smartphones": "product_category",
            "show me headphones": "product_category",
            "i am looking for an affordable laptop for programming": "cheaper_product",
            "show my orders": "show_orders",
            "track my order": "track_order",
            "recommend products for me": "recommend_product",
        }
        for message, expected in cases.items():
            with self.subTest(message=message):
                self.assertEqual(detect_intent(message)[0], expected)

    def test_general_knowledge_questions_are_recognized(self):
        self.assertEqual(
            detect_intent("What is the capital of Japan?")[0],
            "general_knowledge",
        )

    @patch("app.services.public_information_service._get_json")
    def test_capital_question_uses_rest_countries_primary_provider(self, mock_get_json):
        mock_get_json.return_value = [
            {"name": {"common": "Japan", "official": "Japan"},
             "capital": ["Tokyo"]}
        ]
        response = get_general_knowledge("What is the capital of Japan?")
        self.assertIn("The capital of Japan is Tokyo.", response)
        self.assertIn("https://restcountries.com/", response)
        self.assertEqual(mock_get_json.call_count, 1)

    @patch("app.services.public_information_service._get_json")
    def test_india_capital_is_new_delhi(self, mock_get_json):
        mock_get_json.return_value = [
            {"name": {"common": "India", "official": "Republic of India"},
             "capital": ["New Delhi"]}
        ]
        response = get_general_knowledge("What is the capital of India?")
        self.assertIn("The capital of India is New Delhi.", response)
        self.assertEqual(mock_get_json.call_count, 1)

    @patch("app.services.public_information_service._get_json")
    def test_capital_lookup_falls_back_to_wikidata(self, mock_get_json):
        mock_get_json.side_effect = [
            requests.ConnectionError("primary provider unavailable"),
            {
                "search": [
                    {"id": "Q17", "label": "Japan", "description": "country in East Asia"}
                ]
            },
            {
                "entities": {
                    "Q17": {
                        "claims": {
                            "P36": [
                                {"mainsnak": {"datavalue": {"value": {"id": "Q1490"}}}}
                            ]
                        }
                    }
                }
            },
            {"entities": {"Q1490": {"labels": {"en": {"value": "Tokyo"}}}}},
        ]
        response = get_general_knowledge("What is the capital of Japan?")
        self.assertIn("The capital of Japan is Tokyo.", response)

    def test_public_product_intents_do_not_require_login(self):
        self.assertNotIn("product_category", LOGIN_REQUIRED_INTENTS)
        self.assertNotIn("cheaper_product", LOGIN_REQUIRED_INTENTS)
        self.assertIn("recommend_product", LOGIN_REQUIRED_INTENTS)
        self.assertIn("show_orders", LOGIN_REQUIRED_INTENTS)

    def test_natural_language_greetings_and_about_are_recognized(self):
        self.assertEqual(detect_intent("hello bro")[0], "greeting")
        self.assertEqual(detect_intent("what can you do?")[0], "assistant_about")

    def test_information_query_extraction_supports_natural_language(self):
        self.assertEqual(
            _query_after_command("Can you tell me the weather in Hyderabad?", ("weather",)),
            "Hyderabad",
        )
        self.assertEqual(
            _query_after_command("What is the meaning of resilience?", ("meaning",)),
            "resilience",
        )

    def test_followup_does_not_match_one_inside_smartphones_or_headphones(self):
        history = [
            "user: Show me all products",
            "assistant: Here are the products I found for you.",
        ]
        self.assertEqual(
            resolve_followup("Do you have any smartphones?", history),
            "Do you have any smartphones?",
        )
        self.assertEqual(
            resolve_followup("Show me headphones", history),
            "Show me headphones",
        )

    def test_followup_only_uses_user_messages_as_context(self):
        history = [
            "user: Show me all products",
            "assistant: Here are the products I found for you.",
        ]
        self.assertEqual(
            resolve_followup("Can you show another one?", history),
            "recommend product",
        )

    def test_hi_is_not_matched_inside_another_word(self):
        self.assertEqual(detect_intent("which laptop is best")[0], "product_category")

    def test_empty_and_unknown_messages(self):
        self.assertEqual(detect_intent("")[0], "unknown")
        self.assertEqual(detect_intent("ff")[0], "unknown")


if __name__ == "__main__":
    unittest.main()
