import unittest
from unittest.mock import patch

from app.services import ml_model_loader
from app.services.ml_intent_scope import (
    INITIAL_ML_INTENTS,
    model_matches_initial_scope,
)


class FakeModel:
    def __init__(self, classes):
        self.classes_ = classes


class FakePipeline:
    def __init__(self, classes):
        self.named_steps = {"classifier": FakeModel(classes)}


class MLIntentScopeTests(unittest.TestCase):
    def test_allowlist_contains_exactly_five_initial_intents(self):
        self.assertEqual(
            set(INITIAL_ML_INTENTS),
            {
                "add_to_cart",
                "view_cart",
                "show_orders",
                "track_order",
                "cancel_order",
            },
        )
        self.assertEqual(len(INITIAL_ML_INTENTS), 5)

    def test_accepts_pipeline_with_exact_five_classes(self):
        self.assertTrue(model_matches_initial_scope(FakePipeline(INITIAL_ML_INTENTS)))

    def test_rejects_model_with_extra_or_missing_classes(self):
        self.assertFalse(
            model_matches_initial_scope(
                FakePipeline((*INITIAL_ML_INTENTS, "greeting"))
            )
        )
        self.assertFalse(
            model_matches_initial_scope(
                FakePipeline(INITIAL_ML_INTENTS[:-1])
            )
        )

    def test_missing_model_falls_back_without_raising(self):
        with patch.object(ml_model_loader, "MODEL_PATH", "missing-model.pkl"),              patch("app.services.ml_model_loader.os.path.exists", return_value=False):
            self.assertIsNone(ml_model_loader.load_model())
            self.assertIsNone(ml_model_loader.get_model()[0])

    def test_incompatible_artifact_is_rejected(self):
        old_model = FakePipeline((*INITIAL_ML_INTENTS, "greeting"))
        with patch.object(ml_model_loader, "MODEL_PATH", "old-model.pkl"),              patch("app.services.ml_model_loader.os.path.exists", return_value=True),              patch("app.services.ml_model_loader.joblib.load", return_value=old_model):
            self.assertIsNone(ml_model_loader.load_model())
            self.assertIsNone(ml_model_loader.get_model()[0])

    def test_valid_artifact_is_loaded(self):
        valid_model = FakePipeline(INITIAL_ML_INTENTS)
        with patch.object(ml_model_loader, "MODEL_PATH", "valid-model.pkl"),              patch("app.services.ml_model_loader.os.path.exists", return_value=True),              patch("app.services.ml_model_loader.joblib.load", return_value=valid_model):
            self.assertIs(ml_model_loader.load_model(), valid_model)
            self.assertIs(ml_model_loader.get_model()[0], valid_model)


if __name__ == "__main__":
    unittest.main()
