import unittest

from app import create_app
from app.extensions import db
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from flask_jwt_extended import create_access_token


class GuestChatSessionIsolationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def headers(self, identity):
        token = create_access_token(identity=identity)
        return {"Authorization": f"Bearer {token}"}

    def post_chat(self, message, guest_token=None, headers=None):
        payload = {"message": message}
        if guest_token is not None:
            payload["guest_session_token"] = guest_token
        return self.client.post(
            "/api/v1/assistant/chat",
            json=payload,
            headers=headers or {},
        )

    def test_guest_token_is_created_then_reused_for_same_session(self):
        first = self.post_chat("hello from guest")
        self.assertEqual(first.status_code, 200)
        token = first.get_json()["guest_session_token"]
        self.assertTrue(token)

        second = self.post_chat("good morning", guest_token=token)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.get_json()["guest_session_token"], token)

        sessions = ChatSession.query.filter_by(user_id=None).all()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(
            ChatMessage.query.filter_by(session_id=sessions[0].id).count(),
            4,
        )

    def test_two_guests_get_separate_sessions_and_histories(self):
        guest_a_first = self.post_chat("hello from guest A")
        token_a = guest_a_first.get_json()["guest_session_token"]
        guest_a_second = self.post_chat("good morning guest A", guest_token=token_a)

        guest_b_first = self.post_chat("hello from guest B")
        token_b = guest_b_first.get_json()["guest_session_token"]
        guest_b_second = self.post_chat("good morning guest B", guest_token=token_b)

        self.assertEqual(guest_a_second.status_code, 200)
        self.assertEqual(guest_b_second.status_code, 200)
        self.assertNotEqual(token_a, token_b)

        sessions = ChatSession.query.filter_by(user_id=None).all()
        self.assertEqual(len(sessions), 2)

        messages_by_session = {
            session.id: [
                item.message
                for item in ChatMessage.query.filter_by(session_id=session.id).all()
            ]
            for session in sessions
        }
        all_guest_a_messages = [
            message
            for messages in messages_by_session.values()
            for message in messages
            if "guest A" in message
        ]
        all_guest_b_messages = [
            message
            for messages in messages_by_session.values()
            for message in messages
            if "guest B" in message
        ]
        self.assertTrue(all_guest_a_messages)
        self.assertTrue(all_guest_b_messages)

        session_a = next(
            session_id
            for session_id, messages in messages_by_session.items()
            if "hello from guest A" in messages
        )
        session_b = next(
            session_id
            for session_id, messages in messages_by_session.items()
            if "hello from guest B" in messages
        )
        self.assertNotEqual(session_a, session_b)
        self.assertNotIn("hello from guest B", messages_by_session[session_a])
        self.assertNotIn("hello from guest A", messages_by_session[session_b])

    def test_unknown_guest_token_is_rejected_without_creating_a_session(self):
        response = self.post_chat("hello", guest_token="not-a-valid-issued-token")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(ChatSession.query.count(), 0)

    def test_authenticated_user_session_ignores_guest_token(self):
        response = self.post_chat(
            "hello from authenticated user",
            guest_token="guest-token-must-not-be-used",
            headers=self.headers("321"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("guest_session_token", response.get_json())

        sessions = ChatSession.query.all()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].user_id, 321)
        self.assertIsNone(sessions[0].guest_token_hash)


if __name__ == "__main__":
    unittest.main()
