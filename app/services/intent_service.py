import re

"""Rule-based intent detection for the web assistant.

Keep intent names aligned with app/services/intent_registry.py. The returned
model-version value identifies the rule set that produced the prediction.
"""


def detect_intent(message: str):
    """Return (intent, confidence_score, model_version)."""
    msg = re.sub(r"\s+", " ", (message or "").lower().strip())

    if not msg:
        return "unknown", 0.0, "rule_v4"

    if any(p in msg for p in (
        "who made you", "who built you", "who created you", "who developed you",
        "who are you", "your name"
    )):
        return "assistant_identity", 0.99, "rule_v4"

    about_patterns = (
        r"\bwhat can you (?:do|help me with|help with)\b",
        r"\bhow can you help(?: me)?\b",
        r"\bwhat (?:services|features) do you offer\b",
        r"\bwhat (?:services and features|capabilities) (?:are available|do you have)\b",
        r"\btell me about your capabilities\b",
        r"\b(?:tell me about|information about) (?:your )?services\b",
        r"\bwhat do you offer\b",
        r"^#?(?:about|help|features)$",
    )
    if any(re.search(pattern, msg) for pattern in about_patterns) or re.search(
        r"\bhelp me with something else\b|\bstart over\b", msg
    ):
        return "assistant_about", 0.98, "rule_v4"

    if re.search(r"\b(explain that|in simpler words|in simpler terms|simpler words)\b", msg):
        return "clarification", 0.90, "rule_v4"

    greeting_patterns = (
        r"^(hi+|hello+|hey+|hii+|heyy+)\b",
        r"^(good morning|good afternoon|good evening|good night)\b",
        r"\bhow are you\b",
        r"\b(thank you|thanks|thx)\b",
        r"^fine[!. ]*$",
    )
    if any(re.search(pattern, msg) for pattern in greeting_patterns):
        return "greeting", 0.96, "rule_v4"

    # Explicit cart actions must not fall through to product catalogue search.
    if re.search(r"\b(add|put|move)\b.*\b(cart|basket)\b", msg):
        return "add_to_cart", 0.96, "rule_v4"
    if re.search(r"\b(cart|basket)\b", msg):
        return "view_cart", 0.94, "rule_v4"

    if re.search(r"\b(in stock|available in stock|stock availability|how many .*available)\b", msg):
        return "product_stock", 0.94, "rule_v4"

    if re.search(r"\b(compare|comparison|difference between|which is better)\b", msg):
        return "product_compare", 0.93, "rule_v4"

    if re.search(r"\b(alternatives?|similar products?|other options)\b", msg):
        return "product_alternatives", 0.92, "rule_v4"

    if re.search(r"\b(details?|specifications?|specs)\b", msg) and re.search(
        r"\b(product|item|laptop|phone|mobile|smartphone|tablet|camera|tv)\b", msg
    ):
        return "product_detail", 0.92, "rule_v4"

    if re.search(r"\b(price|cost|how much)\b", msg) and re.search(
        r"\b(product|item|this|that|it|laptop|phone|mobile|smartphone|tablet|camera|tv)\b",
        msg,
    ):
        return "product_price", 0.92, "rule_v4"

    public_patterns = (
        (r"\b(weather|temperature)\b|\b(is it|will it be) (?:hot|cold|raining|rainy|sunny|windy)\b", "weather"),
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
            return intent, 0.94, "rule_v4"

    if re.search(r"\b(track|tracking)\b", msg):
        return "track_order", 0.92, "rule_v4"

    if re.search(r"\b(order|orders)\b", msg):
        return "show_orders", 0.92, "rule_v4"

    if re.search(
        r"\b(costliest|most expensive|highest[- ]priced|highest price|priciest|dearest)\b",
        msg,
    ):
        return "costliest_product", 0.94, "rule_v4"

    # Explicit recommendation language wins over a bare product-category mention.
    if re.search(
        r"\b(personalized|personalised|my recommendations|recommendations for me|"
        r"based on my (orders|history|purchases)|recommend|recommendation|suggest)\b",
        msg,
    ):
        return "recommend_product", 0.92, "rule_v4"

    # Advice is requirement-led product selection, not price-only filtering.
    if re.search(
        r"\b(help me choose|help choosing|choose a suitable|select a product|"
        r"for programming|for office work|for gaming|for photography|for video editing|"
        r"for graphic design|for students?|for daily use|for work)\b",
        msg,
    ):
        return "product_advice", 0.90, "rule_v4"

    if re.search(
        r"\b(cheapest|cheaper|lowest[- ]priced|lowest price|least expensive)\b",
        msg,
    ):
        return "cheaper_product", 0.94, "rule_v4"

    if re.search(
        r"\b(cheap|affordable|budget|under|below|less than|within|up to|"
        r"between|from|above|over|more than|greater than|at least|minimum price|"
        r"maximum|minimum|max|min)\b",
        msg,
    ):
        return "cheaper_product", 0.92, "rule_v4"

    category_pattern = (
        r"\b(phones?|mobiles?|smartphones?|laptops?|computers?|"
        r"earbuds?|headphones?|tablets?|watches?|electronics|accessories|"
        r"tvs?|televisions?|monitors?|printers?|cameras?|projectors?|"
        r"gaming consoles?|playstation|xbox)\b"
    )
    if re.search(category_pattern, msg):
        return "product_category", 0.90, "rule_v4"

    if re.search(
        r"\b(product|products|catalog|catalogue|items|inventory|"
        r"what do you sell|what can i buy)\b",
        msg,
    ):
        return "show_products", 0.90, "rule_v4"

    # Require a meaningful subject; do not send "what is this?" or gibberish to search.
    factual_pattern = (
        r"\b(capital of|what is|what are|who is|where is|when was|"
        r"how does|why does|which country|which city)\s+"
        r"(?!this\b|that\b|it\b|there\b)([a-z0-9][a-z0-9 _'-]{1,})"
    )
    if re.search(factual_pattern, msg):
        return "general_knowledge", 0.82, "rule_v4"

    return "unknown", 0.0, "rule_v4"
