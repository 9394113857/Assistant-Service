"""Intent scopes for the assistant and its initial supervised-ML model.

The runtime/review taxonomy is broader than the first ML model. Keep these
allowlists separate so collecting labels for the full assistant never expands
the classes accepted by the initial model artifact.
"""

SUPPORTED_REVIEW_INTENTS = (
    "add_to_cart",
    "assistant_about",
    "assistant_identity",
    "cancel_order",
    "cheaper_product",
    "clarification",
    "costliest_product",
    "general_knowledge",
    "greeting",
    "product_advice",
    "product_alternatives",
    "product_category",
    "product_compare",
    "product_detail",
    "product_price",
    "product_stock",
    "recommend_product",
    "show_orders",
    "show_products",
    "track_order",
    "unknown",
    "view_cart",
    "weather",
)

INITIAL_ML_INTENTS = (
    "add_to_cart",
    "view_cart",
    "show_orders",
    "track_order",
    "cancel_order",
)


def model_matches_initial_scope(candidate):
    """Return True only when a loaded sklearn pipeline has exactly the five ML classes."""
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
