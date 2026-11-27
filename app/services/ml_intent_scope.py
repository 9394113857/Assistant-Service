"""Initial supervised-ML intent allowlist.

This scope applies only to the first ML model. The existing rule-based assistant
continues to support its other intents until later phases explicitly expand ML.
"""

INITIAL_ML_INTENTS = (
    "add_to_cart",
    "view_cart",
    "show_orders",
    "track_order",
    "cancel_order",
)


def model_matches_initial_scope(candidate):
    """Return True only when a loaded sklearn pipeline has exactly these classes."""
    classes = getattr(candidate, "classes_", None)

    if classes is None:
        named_steps = getattr(candidate, "named_steps", {})
        classifier = named_steps.get("classifier") if hasattr(named_steps, "get") else None
        classes = getattr(classifier, "classes_", None)

    if classes is None:
        return False

    try:
        loaded_classes = {str(label) for label in classes}
    except TypeError:
        return False

    return loaded_classes == set(INITIAL_ML_INTENTS)
