import re

"""Rule-based intent detection for the web assistant.

Keep intent names aligned with app/services/intent_registry.py.
The ML classifier can be introduced later behind this stable contract.
"""


def detect_intent(message: str):
    """Return (intent, confidence_score, model_version)."""
    msg = (message or "").lower().strip()
    msg = re.sub(r"\s+", " ", msg)

    if not msg:
        return "unknown", 0.0, "rule_v2"

    # Assistant identity and help
    if any(p in msg for p in (
        "who made you", "who created you", "who developed you",
        "who are you", "your name"
    )):
        return "assistant_identity", 0.99, "rule_v2"

    if re.fullmatch(r"#?(about|help|features)|what can you do[?!.]?", msg):
        return "assistant_about", 0.98, "rule_v2"

    # Greetings and conversational messages (word-boundary matching avoids
    # false positives such as matching "hi" inside "which").
    greeting_patterns = (
        r"^(hi+|hello+|hey+|hii+|heyy+)\b",
        r"^(good morning|good afternoon|good evening|good night)\b",
        r"\bhow are you\b",
        r"\b(thank you|thanks|thx)\b",
        r"^fine[!. ]*$",
    )
    if any(re.search(pattern, msg) for pattern in greeting_patterns):
        return "greeting", 0.96, "rule_v2"

    # Public information requests
    if re.search(r"\b(weather|temperature)\b", msg):
        return "weather", 0.94, "rule_v2"
    if re.search(r"\b(wiki|wikipedia)\b", msg):
        return "wikipedia", 0.94, "rule_v2"
    if re.search(r"\b(movie|film)\b", msg):
        return "movie", 0.94, "rule_v2"
    if re.search(r"\b(book)\b", msg):
        return "book", 0.94, "rule_v2"
    if re.search(r"\b(synonym|synonyms)\b", msg):
        return "synonym", 0.94, "rule_v2"
    if re.search(r"\b(meaning|define|definition)\b", msg):
        return "meaning", 0.94, "rule_v2"
    if re.search(r"\b(news|headlines)\b", msg):
        return "news", 0.94, "rule_v2"
    if re.search(r"\b(joke|jokes)\b", msg):
        return "joke", 0.94, "rule_v2"
    if re.search(r"\b(fact|facts)\b", msg):
        return "random_fact", 0.94, "rule_v2"
    if re.search(r"\b(quote|quotes)\b", msg):
        return "quote", 0.94, "rule_v2"
    if re.search(r"\b(corona|covid|coronastats)\b", msg):
        return "covid_stats", 0.94, "rule_v2"

    # E-commerce intents. Specific actions must be checked before broad
    # product/order terms.
    if re.search(r"\b(track|tracking)\b", msg):
        return "track_order", 0.92, "rule_v2"
    if re.search(r"\b(recommend|recommendation|suggest)\b", msg):
        return "recommend_product", 0.92, "rule_v2"
    if re.search(r"\b(cheap|cheaper|lowest price|low price|affordable|budget|under|below)\b", msg):
        return "cheaper_product", 0.90, "rule_v2"
    if re.search(
        r"\b(phones?|mobiles?|smartphones?|laptops?|computers?|"
        r"earbuds?|headphones?|tablets?|watches?|electronics|accessories)\b",
        msg,
    ):
        return "product_category", 0.88, "rule_v2"
    if re.search(r"\b(order|orders)\b", msg):
        return "show_orders", 0.92, "rule_v2"
    if re.search(
        r"\b(product|products|catalog|catalogue|items|inventory|"
        r"what do you sell|what can i buy)\b",
        msg,
    ):
        return "show_products", 0.90, "rule_v2"

    return "unknown", 0.0, "rule_v2"
