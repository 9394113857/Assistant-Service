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
    """Return a numeric price for sorting, or None when the price is invalid."""
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

    formatted_amount = (
        f"{amount:,.0f}" if amount.is_integer() else f"{amount:,.2f}"
    )
    return f"₹{formatted_amount}"


def _matches_product_query(product, message):
    """Match meaningful query words against the product name/category."""
    ignored_words = {
        "show", "list", "find", "get", "display", "all", "available",
        "some", "me", "the", "for", "with", "please", "i", "want",
        "looking", "search", "products", "product", "items", "category",
        "under", "below", "within", "budget", "cheap", "cheaper",
        "affordable", "lowest", "price", "low",
    }
    query_words = {
        word.rstrip("s")
        for word in re.findall(r"[a-z0-9]+", (message or "").lower())
        if len(word) > 2 and word not in ignored_words
    }
    if not query_words:
        return True

    product_text = " ".join(
        str(product.get(field, "") or "")
        for field in ("name", "category")
    ).lower()
    product_words = {
        word.rstrip("s") for word in re.findall(r"[a-z0-9]+", product_text)
    }
    return any(
        query_word in product_words
        or any(query_word in product_word or product_word in query_word
               for product_word in product_words)
        for query_word in query_words
    )


# ==============================
# PRODUCT REQUEST
# ==============================
def handle_product_request(message=""):
    """Fetch products and apply category/price intent filtering locally."""
    if not PRODUCT_SERVICE_URL:
        return "Product service is not configured. Please check PRODUCT_SERVICE_URL."

    try:
        response = requests.get(
            PRODUCT_SERVICE_URL,
            timeout=PRODUCT_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        products = response.json()

        if not isinstance(products, list):
            return "Product service returned an unexpected response."

        if not products:
            return "No products available right now."

        normalized_message = (message or "").lower()
        category_terms = re.findall(
            r"\\b(phones?|mobiles?|smartphones?|laptops?|computers?|"
            r"earbuds?|headphones?|tablets?|watches?|electronics|accessories)\\b",
            normalized_message,
        )
        if category_terms:
            filtered_products = [
                product for product in products
                if _matches_product_query(product, normalized_message)
            ]
            if not filtered_products:
                return "I couldn't find products matching that category."
            products = filtered_products

        if re.search(
            r"\\b(cheap|cheaper|lowest price|low price|affordable|budget|under|below)\\b",
            normalized_message,
        ):
            products = sorted(
                products,
                key=lambda product: (
                    _product_price(product) is None,
                    _product_price(product) if _product_price(product) is not None else float("inf"),
                ),
            )

        result = "Here are the matching products:\\n"
        for product in products[:5]:
            name = product.get("name", "Unknown")
            price = _format_product_price(product.get("price"))
            category = product.get("category")
            category_label = f" | Category: {category}" if category else ""
            result += f"- {name} | Price: {price}{category_label}\\n"

        return result.rstrip()

    except requests.Timeout:
        return "Product service took too long to respond. Please try again."
    except requests.RequestException:
        return "Product service is temporarily unavailable. Please try again later."
    except (ValueError, TypeError):
        return "Product service returned invalid product data."


# ==============================
# ORDER REQUEST
# ==============================
def handle_order_request(user_id: int):

    try:

        token = request.headers.get("Authorization")

        headers = {}

        if token:
            headers["Authorization"] = token

        response = requests.get(
            f"{ORDER_SERVICE_URL}/{user_id}",
            headers=headers
        )

        if response.status_code == 401:
            return "Please login to access your orders."

        if response.status_code != 200:
            return "Could not fetch orders."

        orders = response.json()

        if not orders:
            return "You have no orders."

        result = "Your recent orders:\\n"

        for o in orders[:5]:

            order_id = o.get("order_id") or o.get("id")
            status = o.get("status", "unknown")

            result += f"- Order #{order_id} | Status: {status}\\n"

        return result

    except Exception:
        return "Order service unavailable."


# ==============================
# RECOMMENDATION REQUEST
# ==============================
def handle_recommendation_request(user_id: int):

    try:

        token = request.headers.get("Authorization")

        headers = {}

        if token:
            headers["Authorization"] = token

        response = requests.get(
            f"{RECO_SERVICE_URL}/{user_id}",
            headers=headers
        )

        if response.status_code != 200:
            return "Recommendation service unavailable."

        recos = response.json()

        if not recos:
            return "No recommendations available yet."

        result = "Recommended for you:\\n"

        for r in recos[:5]:

            product_id = r.get("product_id")

            result += f"- Product ID: {product_id}\\n"

        return result

    except Exception:
        return "Could not fetch recommendations."
