import re


_PRODUCT_LINE_PATTERNS = (
    re.compile(r"^\s*[-*]\s*(.+?)\s*\|\s*Price\s*:", re.IGNORECASE),
    re.compile(r"^\s*[-*]\s*(.+?)\s*[—–-]\s*₹", re.IGNORECASE),
)


def _assistant_products(previous_messages):
    """Extract product names from the latest assistant catalogue response."""
    for previous in reversed(previous_messages or []):
        previous_text = str(previous).strip()
        if ":" in previous_text:
            role, text = previous_text.split(":", 1)
            if role.strip().lower() != "assistant":
                continue
        else:
            text = previous_text

        names = []
        for line in text.splitlines():
            for pattern in _PRODUCT_LINE_PATTERNS:
                match = pattern.match(line)
                if match:
                    name = match.group(1).strip()
                    if name and name not in names:
                        names.append(name)
                    break
        if names:
            return names
    return []


def resolve_followup(message: str, previous_messages: list) -> str:
    """Resolve clear product references using the latest assistant product list."""
    message_text = (message or "").strip()
    message_lower = message_text.lower()
    products = _assistant_products(previous_messages)

    # Resolve explicit ordinal references such as "the first product".
    ordinal_match = re.search(r"\b(?:the\s+)?(first|second|third)\s+(?:product|item|one)\b", message_lower)
    if ordinal_match and products:
        index = {"first": 0, "second": 1, "third": 2}[ordinal_match.group(1)]
        if index < len(products):
            return re.sub(
                r"\b(?:the\s+)?(first|second|third)\s+(?:product|item|one)\b",
                products[index],
                message_text,
                count=1,
                flags=re.IGNORECASE,
            )

    # Resolve "this product", "that item", and similar references only when
    # the preceding assistant message contains a concrete product list.
    reference_match = re.search(
        r"\b(this|that|the)\s+(?:product|item|one)\b|\bthis one\b|\bthat one\b",
        message_lower,
    )
    if reference_match and products:
        return re.sub(
            r"\b(this|that|the)\s+(?:product|item|one)\b|\bthis one\b|\bthat one\b",
            products[0],
            message_text,
            count=1,
            flags=re.IGNORECASE,
        )

    # Explicit product/category/order wording is already meaningful.
    if re.search(
        r"\b(product|products|item|items|order|orders|recommend|"
        r"phone|phones|mobile|mobiles|smartphone|smartphones|laptop|laptops|"
        r"computer|computers|headphone|headphones|earbud|earbuds|tablet|tablets)\b",
        message_lower,
    ):
        return message_text

    # Keep the existing narrow "another one" follow-up behavior.
    if re.search(r"\b(one|another one)\b", message_lower):
        for previous in reversed(previous_messages or []):
            previous_text = str(previous).strip()
            if ":" in previous_text:
                role, text = previous_text.split(":", 1)
                if role.strip().lower() != "user":
                    continue
            else:
                text = previous_text
            if re.search(r"\b(product|products|item|items)\b", text.lower()):
                return "recommend product"

    return message_text
