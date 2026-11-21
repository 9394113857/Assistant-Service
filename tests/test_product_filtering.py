import unittest
from unittest.mock import patch

from app.services import tool_router


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class ProductFilteringTests(unittest.TestCase):
    def setUp(self):
        self.products = [
            {"id": 1, "name": "Gaming Laptop Pro", "price": 75000, "category": "Electronics"},
            {"id": 2, "name": "Laptop", "price": 55000, "category": "Electronics"},
            {"id": 3, "name": "Item-21", "price": 21000, "category": "Smart Phones"},
            {"id": 4, "name": "Budget Phone", "price": 15000, "category": "Smart Phones"},
            {"id": 5, "name": "Exactly Twenty Thousand", "price": 20000, "category": "Electronics"},
        ]
        self.url_patch = patch.object(tool_router, "PRODUCT_SERVICE_URL", "https://products.test/list")
        self.url_patch.start()
        self.request_patch = patch(
            "app.services.tool_router.requests.get",
            return_value=FakeResponse(self.products),
        )
        self.request_patch.start()

    def tearDown(self):
        self.request_patch.stop()
        self.url_patch.stop()

    def test_explicit_budget_excludes_products_above_limit(self):
        response = tool_router.handle_product_request("Find products below ₹20,000")
        self.assertIn("Budget Phone", response)
        self.assertNotIn("Item-21", response)
        self.assertNotIn("Laptop", response)
        self.assertNotIn("Gaming Laptop Pro", response)
        self.assertNotIn("Exactly Twenty Thousand", response)

    def test_category_search_matches_smartphones_without_login_routing(self):
        response = tool_router.handle_product_request("Do you have any smartphones?")
        self.assertIn("Budget Phone", response)
        self.assertIn("Item-21", response)
        self.assertNotIn("Laptop", response)

    def test_cheapest_product_sorts_lowest_price_first(self):
        response = tool_router.handle_product_request("What is your cheapest product?")
        self.assertLess(response.index("Budget Phone"), response.index("Item-21"))
        self.assertLess(response.index("Item-21"), response.index("Laptop"))
        self.assertLess(response.index("Laptop"), response.index("Gaming Laptop Pro"))

    def test_short_budget_suffix_is_parsed(self):
        self.assertEqual(tool_router._extract_price_limit("under 20k"), 20000)
        self.assertEqual(tool_router._extract_price_limit("below ₹1 lakh"), 100000)


if __name__ == "__main__":
    unittest.main()
