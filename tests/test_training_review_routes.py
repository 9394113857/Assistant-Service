import unittest

from app import create_app
from app.extensions import db
from app.models.assistant_training_log import AssistantTrainingLog
from app.services.ml_intent_scope import SUPPORTED_REVIEW_INTENTS
from flask_jwt_extended import create_access_token


class TrainingReviewRouteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.record = AssistantTrainingLog(
            user_id=None,
            user_message="show me my orders",
            predicted_intent="unknown",
            confidence_score=0.21,
            model_version="rule_v3",
        )
        db.session.add(self.record)
        db.session.commit()
        self.record_id = self.record.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def headers(self, role="admin", identity="42"):
        token = create_access_token(
            identity=identity,
            additional_claims={"role": role},
        )
        return {"Authorization": f"Bearer {token}"}

    def test_review_queue_requires_authentication(self):
        response = self.client.get("/api/v1/assistant/training/review-queue")
        self.assertEqual(response.status_code, 401)

    def test_review_queue_rejects_non_admin(self):
        response = self.client.get(
            "/api/v1/assistant/training/review-queue",
            headers=self.headers(role="user"),
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_list_pending_records(self):
        response = self.client.get(
            "/api/v1/assistant/training/review-queue",
            headers=self.headers(),
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["items"][0]["id"], self.record_id)
        self.assertIsNone(payload["items"][0]["actual_intent"])

    def test_admin_can_review_record_and_audit_reviewer(self):
        response = self.client.post(
            f"/api/v1/assistant/training/{self.record_id}/review",
            json={"actual_intent": "show_orders"},
            headers=self.headers(identity="42"),
        )
        self.assertEqual(response.status_code, 200)
        db.session.expire_all()
        saved = db.session.get(AssistantTrainingLog, self.record_id)
        self.assertEqual(saved.actual_intent, "show_orders")
        self.assertEqual(saved.reviewer_user_id, 42)
        self.assertIsNotNone(saved.reviewed_at)

    def test_admin_can_review_all_supported_assistant_intents(self):
        for intent in SUPPORTED_REVIEW_INTENTS:
            record = AssistantTrainingLog(
                user_id=None,
                user_message=f"test message for {intent}",
                predicted_intent="unknown",
                confidence_score=0.0,
                model_version="rule_v4",
            )
            db.session.add(record)
            db.session.commit()

            response = self.client.post(
                f"/api/v1/assistant/training/{record.id}/review",
                json={"actual_intent": intent},
                headers=self.headers(),
            )
            self.assertEqual(response.status_code, 200, intent)
            self.assertEqual(response.get_json()["actual_intent"], intent)

    def test_review_rejects_unknown_intent(self):
        response = self.client.post(
            f"/api/v1/assistant/training/{self.record_id}/review",
            json={"actual_intent": "made_up_intent"},
            headers=self.headers(),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["allowed_intents"],
            sorted(SUPPORTED_REVIEW_INTENTS),
        )

    def test_record_cannot_be_reviewed_twice(self):
        url = f"/api/v1/assistant/training/{self.record_id}/review"
        first = self.client.post(
            url,
            json={"actual_intent": "show_orders"},
            headers=self.headers(),
        )
        second = self.client.post(
            url,
            json={"actual_intent": "track_order"},
            headers=self.headers(),
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 409)


if __name__ == "__main__":
    unittest.main()
