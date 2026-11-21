import os
import re

import requests
from flask import request

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL")
CART_SERVICE_URL = os.getenv("CART_SERVICE_URL")
RECO_SERVICE_URL = os.getenv("RECO_SERVICE_URL")

PRODUCT_REQUEST_TIMEOUT = 10


def _product_price(product):
    """Return a numeric price for sorting/filtering, or None when invalid."""
    try:
        value = product.get("price")
        if value is None:
            return None
        if isinstance(value, str):
            value = re.sub(r"[^0-9.]", "", value)
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_product_price(value):
    """Format product prices consistently as Indian Rupees."""
    amount = _product_price({"price": value})
    if amount is None:
        return str(value) if value is not None else "N/A"
    formatted_amount = f"{amount:,.0f}" if amount.is_integer() else f"{amount:,.2f}"
    return f"₹{formatted_amount}"


def _normalize_category(value):
    return " ".join(re.findall(r"[a-z0-9]+", str(value or "").lower()))


def _matches_product_query(product, message, catalog_categories=None):
    """Match requested categories using catalogue labels and safe aliases."""
    text = (message or "").lower()
    category = _normalize_category(product.get("category"))
    product_text = " ".join(
        str(product.get(field, "") or "")
        for field in ("name", "category")
    ).lower()
    product_words = {
        word.rstrip("s") for word in re.findall(r"[a-z0-9]+", product_text)
    }

    # Prefer exact category labels that actually exist in the current catalogue.
    requested_catalog_categories = set()
    for label in catalog_categories or []:
        normalized = _normalize_category(label)
        if normalized and re.search(
            r"\b" + re.escape(normalized).replace(r"\ ", r"\s+") + r"\b",
            text,
        ):
            requested_catalog_categories.add(normalized)

    if requested_catalog_categories:
        return category in requested_catalog_categories

    alias_patterns = {
        r"\bsmart[\s-]*phones?\b": {"smart", "smartphone", "phone", "mobile", "cellphone"},
        r"\bmobile[\s-]*phones?\b": {"mobile", "phone", "smartphone", "cellphone"},
        r"\bphones?\b": {"phone", "mobile", "smartphone", "cellphone"},
        r"\bmobiles?\b": {"mobile", "phone", "smartphone", "cellphone"},
        r"\blaptops?\b": {"laptop", "computer", "notebook"},
        r"\bcomputers?\b": {"computer", "laptop", "notebook"},
        r"\bheadphones?\b": {"headphone", "headset", "earphone", "earbud"},
        r"\bearbuds?\b": {"earbud", "earphone", "headphone"},
        r"\btablets?\b": {"tablet", "ipad"},
        r"\bsmart[\s-]*watches?\b": {"smartwatch", "watch"},
        r"\bwatches?\b": {"watch", "smartwatch"},
        r"\belectronics\b": {"electronics"},
        r"\baccessories\b": {"accessory", "accessories"},
        r"\b(tvs?|televisions?)\b": {"tv", "television"},
        r"\bmonitors?\b": {"monitor", "display"},
        r"\bprinters?\b": {"printer"},
        r"\bcameras?\b": {"camera", "dslr", "mirrorless"},
        r"\b(gaming consoles?|playstation|xbox)\b": {"console", "playstation", "xbox"},
        r"\bprojectors?\b": {"projector"},
    }

    requested_aliases = set()
    for pattern, aliases in alias_patterns.items():
        if re.search(pattern, text):
            requested_aliases.update(aliases)

    if requested_aliases:
        return bool(product_words.intersection(requested_aliases))

    # Conservative fallback for a product name explicitly mentioned by the user.
    ignored_words = {
        "show", "list", "find", "get", "display", "all", "available",
        "some", "me", "the", "for", "with", "please", "i", "want",
        "looking", "search", "products", "product", "items", "category",
        "under", "below", "within", "budget", "cheap", "cheapest", "cheaper",
        "costliest", "expensive", "priciest", "affordable", "lowest", "highest",
        "price", "low", "less", "than", "up", "to", "over", "above", "between",
        "from", "and", "maximum", "minimum", "recommend", "recommendation",
        "suggest", "do", "you", "have", "any", "is", "your", "what", "are",
        "a", "an", "programming", "office", "work", "daily", "usage",
    }
    query_words = {
        word.rstrip("s")
        for word in re.findall(r"[a-z0-9]+", text)
        if len(word) > 2 and word not in ignored_words
    }
    if not query_words:
        return True
    return bool(query_words.intersection(product_words))


def _parse_price_amount(value, unit=""):
    amount = float(str(value).replace(",", ""))
    unit = (unit or "").lower()
    if unit in {"k", "thousand"}:
        amount *= 1000
    elif unit in {"lakh", "lac", "l"}:
        amount *= 100000
    return amount


def _extract_price_bounds(message):
    """Extract a lower/upper price range from common customer phrasing."""
    text = (message or "").lower()

    amount = r"(?:₹|rs\.?|inr)?\s*(\d[\d,]*(?:\.\d+)?)\s*(k|thousand|lakh|lac|l)?"

    between_match = re.search(
        r"\bbetween\s+" + amount + r"\s+(?:and|to|-)\s+" + amount + r"\b",
        text,
    )
    if between_match:
        lower = _parse_price_amount(between_match.group(1), between_match.group(2))
        upper = _parse_price_amount(between_match.group(3), between_match.group(4))
        return {
            "lower": min(lower, upper),
            "upper": max(lower, upper),
            "lower_inclusive": True,
            "upper_inclusive": True,
        }

    # Also accept shorthand ranges such as "₹20k-₹50k".
    shorthand_match = re.search(
        r"(?<![a-z0-9])" + amount + r"\s*(?:-|to)\s*" + amount + r"\b",
        text,
    )
    if shorthand_match:
        lower = _parse_price_amount(shorthand_match.group(1), shorthand_match.group(2))
        upper = _parse_price_amount(shorthand_match.group(3), shorthand_match.group(4))
        return {
            "lower": min(lower, upper),
            "upper": max(lower, upper),
            "lower_inclusive": True,
            "upper_inclusive": True,
        }

    bound_match = re.search(
        r"\b(under|below|less than|up to|within|maximum(?: budget)?(?: of)?|"
        r"max(?: budget)?(?: of)?|above|over|more than|greater than|at least|"
        r"minimum(?: budget)?(?: of)?|min(?: budget)?(?: of)?|budget(?: of)?)\b\s*" + amount,
        text,
    )
    if not bound_match:
        return None

    operator = bound_match.group(1)
    value = _parse_price_amount(bound_match.group(2), bound_match.group(3))
    if operator in {"above", "over", "more than", "greater than"}:
        return {
            "lower": value,
            "upper": None,
            "lower_inclusive": False,
            "upper_inclusive": True,
        }
    if operator.startswith("at least") or operator.startswith("minimum") or operator.startswith("min"):
        return {
            "lower": value,
            "upper": None,
            "lower_inclusive": True,
            "upper_inclusive": True,
        }
    if operator in {"up to", "within"} or operator.startswith("maximum") or operator.startswith("max") or operator.startswith("budget"):
        return {
            "lower": None,
            "upper": value,
            "lower_inclusive": True,
            "upper_inclusive": True,
        }
    return {
        "lower": None,
        "upper": value,
        "lower_inclusive": True,
        "upper_inclusive": False,
    }


def _extract_price_limit(message):
    """Backward-compatible helper returning the requested single price bound."""
    bounds = _extract_price_bounds(message)
    if not bounds:
        return None
    return bounds["upper"] if bounds["upper"] is not None else bounds["lower"]



# Cross-sell only from major products. Small accessories never trigger another
# recommendation carousel, which keeps the shopping conversation lightweight.
_RELATED_PRODUCT_TERMS = {
    "smartphone": ("case", "cover", "screen protector", "tempered glass", "charger", "power bank", "earbuds", "headphones"),
    "laptop": ("mouse", "keyboard", "laptop bag", "sleeve", "cooling pad", "usb hub", "laptop stand", "external drive"),
    "tv": ("soundbar", "speaker", "hdmi cable", "tv mount", "wall mount", "streaming stick"),
    "monitor": ("monitor arm", "hdmi cable", "webcam", "speaker"),
    "printer": ("ink", "toner", "printer paper"),
    "camera": ("tripod", "memory card", "camera bag", "camera lens"),
    "gaming console": ("controller", "gaming headset", "game"),
    "projector": ("projector screen", "hdmi cable", "mount", "speaker"),
}

def _major_product_family(product):
    text = " ".join(str(product.get(field, "") or "") for field in ("name", "category", "description")).lower()
    patterns = (
        ("smartphone", r"\b(smart ?phones?|mobile phones?|cell ?phones?)\b"),
        ("laptop", r"\b(laptop|notebook computer)\\b"),
        ("tv", r"\b(tv|television|smart tv)\\b"),
        ("monitor", r"\b(monitor|display)\\b"),
        ("printer", r"\b(printer)\\b"),
        ("camera", r"\b(camera|dslr|mirrorless)\\b"),
        ("gaming console", r"\b(playstation|xbox|nintendo switch|gaming console)\\b"),
        ("projector", r"\b(projector)\\b"),
    )
    for family, pattern in patterns:
        if re.search(pattern, text):
            return family
    return None


def _related_products(products, catalogue):
    """Return a few in-catalogue add-ons for selected major products only."""
    families = {
        family
        for product in products
        if isinstance(product, dict)
        for family in [_major_product_family(product)]
        if family
    }
    if not families:
        return []

    terms = tuple(term for family in families for term in _RELATED_PRODUCT_TERMS[family])
    selected_ids = {str(p.get("id")) for p in products if p.get("id") is not None}
    selected_names = {str(p.get("name", "")).strip().lower() for p in products}
    suggestions = []
    seen = set()
    for candidate in catalogue:
        if not isinstance(candidate, dict):
            continue
        candidate_id = str(candidate.get("id")) if candidate.get("id") is not None else None
        candidate_name = str(candidate.get("name", "")).strip()
        candidate_text = " ".join(
            str(candidate.get(field, "") or "")
            for field in ("name", "category", "description")
        ).lower()
        if not candidate_name or candidate_name.lower() in selected_names:
            continue
        if candidate_id and candidate_id in selected_ids:
            continue
        if not any(term in candidate_text for term in terms):
            continue
        key = candidate_id or candidate_name.lower()
        if key in seen:
            continue
        seen.add(key)
        suggestions.append(candidate)
        if len(suggestions) == 3:
            break
    return suggestions

def handle_product_request(message=""):
    """Fetch catalogue products and apply category, budget, range and price ranking."""
    if not PRODUCT_SERVICE_URL:
        return "Product service is not configured. Please check PRODUCT_SERVICE_URL."

    try:
        response = requests.get(PRODUCT_SERVICE_URL, timeout=PRODUCT_REQUEST_TIMEOUT)
        response.raise_for_status()
        products = response.json()

        if not isinstance(products, list):
            return "Product service returned an unexpected response."
        if not products:
            return "No products available right now."

        all_products = products

        normalized_message = (message or "").lower()
        catalog_categories = list(dict.fromkeys(
            product.get("category")
            for product in products
            if isinstance(product, dict) and product.get("category")
        ))

        # Apply a category filter only when the customer actually names one.
        category_patterns = (
            r"\bsmart[\s-]*phones?\b", r"\bmobile[\s-]*phones?\b",
            r"\bphones?\b", r"\bmobiles?\b", r"\blaptops?\b",
            r"\bcomputers?\b", r"\bheadphones?\b", r"\bearbuds?\b",
            r"\btablets?\b", r"\bsmart[\s-]*watches?\b", r"\bwatches?\b",
            r"\belectronics\b", r"\baccessories\b", r"\b(tvs?|televisions?)\b",
            r"\bmonitors?\b", r"\bprinters?\b", r"\bcameras?\b",
            r"\b(gaming consoles?|playstation|xbox)\b", r"\bprojectors?\b",
        )
        has_known_category = any(
            re.search(pattern, normalized_message) for pattern in category_patterns
        )
        has_catalog_category = any(
            re.search(
                r"\b" + re.escape(_normalize_category(category)).replace(r"\ ", r"\s+") + r"\b",
                normalized_message,
            )
            for category in catalog_categories
            if _normalize_category(category)
        )
        if has_known_category or has_catalog_category:
            products = [
                product for product in products
                if _matches_product_query(product, normalized_message, catalog_categories)
            ]
            if not products:
                return "I couldn't find products matching that category in the current catalogue."

        price_bounds = _extract_price_bounds(normalized_message)
        if price_bounds:
            lower = price_bounds["lower"]
            upper = price_bounds["upper"]
            products = [
                product for product in products
                if _product_price(product) is not None
                and (
                    lower is None
                    or (
                        _product_price(product) >= lower
                        if price_bounds["lower_inclusive"]
                        else _product_price(product) > lower
                    )
                )
                and (
                    upper is None
                    or (
                        _product_price(product) <= upper
                        if price_bounds["upper_inclusive"]
                        else _product_price(product) < upper
                    )
                )
            ]
            if not products:
                if lower is not None and upper is not None:
                    range_label = (
                        f"between {_format_product_price(lower)} and "
                        f"{_format_product_price(upper)}"
                    )
                elif upper is not None:
                    range_label = (
                        f"at or below {_format_product_price(upper)}"
                        if price_bounds["upper_inclusive"]
                        else f"below {_format_product_price(upper)}"
                    )
                else:
                    range_label = (
                        f"at or above {_format_product_price(lower)}"
                        if price_bounds["lower_inclusive"]
                        else f"above {_format_product_price(lower)}"
                    )
                return (
                    f"No products were found {range_label} in the selected category. "
                    "Try a different budget or category."
                )

        costliest = re.search(
            r"\b(costliest|most expensive|highest[- ]priced|highest price|priciest|dearest)\b",
            normalized_message,
        )
        cheapest = re.search(
            r"\b(cheapest|cheaper|lowest[- ]priced|lowest price|least expensive)\b",
            normalized_message,
        )

        if costliest:
            products = sorted(
                products,
                key=lambda product: (
                    _product_price(product) is None,
                    -_product_price(product) if _product_price(product) is not None else 0,
                ),
            )
            heading = "Here are the highest-priced matching products:"
        elif cheapest or price_bounds:
            products = sorted(
                products,
                key=lambda product: (
                    _product_price(product) is None,
                    _product_price(product) if _product_price(product) is not None else float("inf"),
                ),
            )
            heading = "Here are the matching products, sorted by lowest price:"
        else:
            heading = "Here are the matching products:"

        result = heading + "\n"
        for product in products[:10]:
            name = product.get("name", "Unknown")
            price = _format_product_price(product.get("price"))
            category = product.get("category")
            category_label = f" | Category: {category}" if category else ""
            result += f"- {name} | Price: {price}{category_label}\n"

        # Keep add-ons out of the main results. The storefront chat UI renders
        # this marked section as a collapsed, customer-controlled disclosure.
        related = _related_products(products[:10], catalogue=all_products)
        if related:
            result += "\n__RELATED_PRODUCTS__\nYou may also need (optional):\n"
            for product in related:
                name = product.get("name", "Unknown")
                price = _format_product_price(product.get("price"))
                category = product.get("category")
                category_label = f" | Category: {category}" if category else ""
                result += f"- {name} | Price: {price}{category_label}\n"
        return result.rstrip()

    except requests.Timeout:
        return "Product service took too long to respond. Please try again."
    except requests.RequestException:
        return "Product service is temporarily unavailable. Please try again later."
    except (ValueError, TypeError):
        return "Product service returned invalid product data."


def handle_order_request(user_id: int):
    try:
        token = request.headers.get("Authorization")
        headers = {"Authorization": token} if token else {}
        response = requests.get(
            f"{ORDER_SERVICE_URL}/{user_id}",
            headers=headers,
            timeout=PRODUCT_REQUEST_TIMEOUT,
        )
        if response.status_code == 401:
            return "Please login to access your orders."
        if response.status_code != 200:
            return "Could not fetch orders."
        orders = response.json()
        if not orders:
            return "You have no orders."
        result = "Your recent orders:\n"
        for order in orders[:5]:
            order_id = order.get("order_id") or order.get("id")
            status = order.get("status", "unknown")
            result += f"- Order #{order_id} | Status: {status}\n"
        return result
    except Exception:
        return "Order service unavailable."


def handle_recommendation_request(user_id: int):
    try:
        token = request.headers.get("Authorization")
        headers = {"Authorization": token} if token else {}
        response = requests.get(
            f"{RECO_SERVICE_URL}/{user_id}",
            headers=headers,
            timeout=PRODUCT_REQUEST_TIMEOUT,
        )
        if response.status_code != 200:
            return "Recommendation service unavailable."
        recommendations = response.json()
        if not recommendations:
            return "No recommendations available yet."
        result = "Recommended for you:\n"
        for recommendation in recommendations[:5]:
            result += f"- Product ID: {recommendation.get('product_id')}\n"
        return result
    except Exception:
        return "Could not fetch recommendations."
