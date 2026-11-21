import re

"""Rule-based intent detection for the web assistant.

Keep intent names aligned with app/services/intent_registry.py.
"""


def detect_intent(message: str):
    """Return (intent, confidence_score, model_version)."""
    msg = re.sub(r"\s+", " ", (message or "").lower().strip())

    if not msg:
        return "unknown", 0.0, "rule_v3"

    # Assistant identity and help
    if any(p in msg for p in (
        "who made you", "who created you", "who developed you",
        "who are you", "your name"
    )):
        return "assistant_identity", 0.99, "rule_v3"

    if re.fullmatch(r"#?(about|help|features)|what can you do[?!.]?", msg):
        return "assistant_about", 0.98, "rule_v3"

    # Greetings and conversational messages
    greeting_patterns = (
        r"^(hi+|hello+|hey+|hii+|heyy+)\b",
        r"^(good morning|good afternoon|good evening|good night)\b",
        r"\bhow are you\b",
        r"\b(thank you|thanks|thx)\b",
        r"^fine[!. ]*$",
    )
    if any(re.search(pattern, msg) for pattern in greeting_patterns):
        return "greeting", 0.96, "rule_v3"

    # Explicit public-information commands
    public_patterns = (
        (r"\b(weather|temperature)\b", "weather"),
        (r"\b(wiki|wikipedia)\b", "wikipedia"),
        (r"\b(movie|film)\b", "movie"),
        (r"\b(book)\b", "book"),
        (r"\b(synonym|synonyms)\b", "synonym"),
        (r"\b(meaning|define|definition)\b", "meaning"),
        (r"\b(news|headlines)\b", "news"),
        (r"\b(joke|jokes)\b", "joke"),
        (r"\b(fact|facts)\b", "random_fact"),
        (r"\b(quote|quotes)\b", "quote"),
        (r"\b(corona|covid|coronastats)\b", "covid_stats"),
    )
    for pattern, intent in public_patterns:
        if re.search(pattern, msg):
            return intent, 0.94, "rule_v3"

    # Private commerce actions are deliberately distinct from public catalogue search.
    if re.search(r"\b(track|tracking)\b", msg):
        return "track_order", 0.92, "rule_v3"

    if re.search(r"\b(order|orders)\b", msg):
        return "show_orders", 0.92, "rule_v3"

    # Product price ranking: detect highest-price requests before budget/category rules.
    if re.search(
        r"\b(costliest|most expensive|highest[- ]priced|highest price|priciest|dearest)\b",
        msg,
    ):
        return "costliest_product", 0.94, "rule_v3"

    if re.search(
        r"\b(cheapest|cheaper|lowest[- ]priced|lowest price|least expensive)\b",
        msg,
    ):
        return "cheaper_product", 0.94, "rule_v3"

    # Budget and price-range requests stay public product searches.
    if re.search(
        r"\b(cheap|affordable|budget|under|below|less than|within|up to|"
        r"between|from|above|over|more than|greater than|at least|minimum price|"
        r"maximum|minimum|max|min)\b",
        msg,
    ):
        return "cheaper_product", 0.92, "rule_v3"

    category_pattern = (
        r"\b(phones?|mobiles?|smartphones?|laptops?|computers?|"
        r"earbuds?|headphones?|tablets?|watches?|electronics|accessories)\b"
    )
    if re.search(category_pattern, msg):
        # Generic product advice/search is public. Only personalized requests
        # without a concrete category go through the login-protected recommender.
        return "product_category", 0.90, "rule_v3"

    if re.search(
        r"\b(personalized|personalised|my recommendations|recommendations for me|"
        r"based on my (orders|history|purchases))\b",
        msg,
    ):
        return "recommend_product", 0.92, "rule_v3"

    if re.search(r"\b(recommend|recommendation|suggest)\b", msg):
        return "recommend_product", 0.90, "rule_v3"

    if re.search(
        r"\b(product|products|catalog|catalogue|items|inventory|"
        r"what do you sell|what can i buy)\b",
        msg,
    ):
        return "show_products", 0.90, "rule_v3"

    # General factual questions, such as "What is the capital of Japan?"
    if re.search(
        r"\b(capital of|what is|what are|who is|where is|when was|"
        r"how does|why does|which country|which city)\b",
        msg,
    ):
        return "general_knowledge", 0.82, "rule_v3"

    return "unknown", 0.0, "rule_v3"
