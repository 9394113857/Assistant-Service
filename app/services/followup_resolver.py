import re


def resolve_followup(message: str, previous_messages: list) -> str:
    """Resolve short follow-ups without matching words inside product names."""
    message_lower = (message or "").lower().strip()

    # Explicit product, category, order, or recommendation wording is already
    # meaningful. Do not rewrite it based on older conversation turns.
    if re.search(
        r"\b(product|products|item|items|order|orders|recommend|"
        r"phone|phones|mobile|mobiles|smartphone|smartphones|laptop|laptops|"
        r"computer|computers|headphone|headphones|earbud|earbuds|tablet|tablets)\b",
        message_lower,
    ):
        return message

    # Only user messages establish context. Assistant replies often contain
    # generic words such as "products" and must not drive intent resolution.
    for previous in reversed(previous_messages or []):
        previous_text = str(previous).strip()
        if ":" in previous_text:
            role, text = previous_text.split(":", 1)
            if role.strip().lower() != "user":
                continue
            text = text.strip().lower()
        else:
            text = previous_text.lower()

        if not re.search(r"\b(product|products|item|items)\b", text):
            continue

        # Match the standalone pronoun "one", never the letters inside
        # "smartphones", "headphones", or other product names.
        if re.search(r"\b(one|another one)\b", message_lower):
            return "recommend product"

        if re.search(r"\b(cheapest|cheap|cheaper|affordable|budget)\b", message_lower):
            return message

    return message
