import unittest
from unittest.mock import patch

from app import create_app
from flask_jwt_extended import create_access_token


class AssistantChatIdentityTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

    def headers(self, identity):
        with self.app.app_context():
            token = create_access_token(identity=identity)
        return {"Authorization": f"Bearer {token}"}

    @patch("app.routes.assistant_routes.process_user_message")
    def test_guest_request_ignores_client_supplied_user_id(self, process_message):
        process_message.return_value = {
            "response": "Hello",
            "intent": "greeting",
            "confidence": 0.96,
            "model_version": "rule_v4",
        }

        response = self.client.post(
            "/api/v1/assistant/chat",
            json={"user_id": 9876, "message": "Hello"},
        )

        self.assertEqual(response.status_code, 200)
        process_message.assert_called_once_with(None, "Hello")

    @patch("app.routes.assistant_routes.process_user_message")
    def test_authenticated_request_uses_jwt_identity_not_body_user_id(self, process_message):
        process_message.return_value = {
            "response": "Your orders",
            "intent": "show_orders",
            "confidence": 0.92,
            "model_version": "rule_v4",
        }

        response = self.client.post(
            "/api/v1/assistant/chat",
            json={"user_id": 9876, "message": "Show my orders"},
            headers=self.headers("123"),
        )

        self.assertEqual(response.status_code, 200)
        process_message.assert_called_once_with(123, "Show my orders")

    def test_authenticated_request_rejects_non_numeric_jwt_identity(self):
        response = self.client.post(
            "/api/v1/assistant/chat",
            json={"message": "Show my orders"},
            headers=self.headers("not-a-user-id"),
        )

        self.assertEqual(response.status_code, 401)

    def test_invalid_bearer_token_is_rejected(self):
        response = self.client.post(
            "/api/v1/assistant/chat",
            json={"message": "Hello"},
            headers={"Authorization": "Bearer invalid-token"},
        )

        self.assertEqual(response.status_code, 401)

    def test_chat_requires_a_non_empty_message(self):
        response = self.client.post(
            "/api/v1/assistant/chat",
            json={"message": "   "},
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
