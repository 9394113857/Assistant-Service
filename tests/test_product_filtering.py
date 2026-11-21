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

    def test_headphones_search_does_not_return_smartphones(self):
        response = tool_router.handle_product_request("Show me headphones")
        self.assertEqual(
            response,
            "I couldn't find products matching that category in the current catalogue.",
        )

    def test_laptop_search_returns_laptops(self):
        response = tool_router.handle_product_request("Show me laptops")
        self.assertIn("Laptop", response)
        self.assertIn("Gaming Laptop Pro", response)
        self.assertNotIn("Item-21", response)

    def test_cheapest_product_sorts_lowest_price_first(self):
        response = tool_router.handle_product_request("What is your cheapest product?")
        self.assertLess(response.index("Budget Phone"), response.index("Item-21"))
        self.assertLess(response.index("Item-21"), response.index("Laptop"))
        self.assertLess(response.index("Laptop"), response.index("Gaming Laptop Pro"))

    def test_costliest_product_sorts_highest_price_first(self):
        response = tool_router.handle_product_request("What is your costliest product?")
        self.assertLess(response.index("Gaming Laptop Pro"), response.index("Laptop"))
        self.assertLess(response.index("Laptop"), response.index("Item-21"))

    def test_most_expensive_smartphone_respects_category(self):
        response = tool_router.handle_product_request("What is the most expensive smartphone?")
        self.assertIn("Item-21", response)
        self.assertIn("Budget Phone", response)
        self.assertNotIn("Laptop", response)
        self.assertLess(response.index("Item-21"), response.index("Budget Phone"))

    def test_smartphones_under_budget_filter_category_and_price(self):
        response = tool_router.handle_product_request("Show smart phones under ₹22,000")
        self.assertIn("Item-21", response)
        self.assertIn("Budget Phone", response)
        self.assertNotIn("Laptop", response)
        self.assertNotIn("Gaming Laptop Pro", response)

    def test_category_budget_with_no_matching_products_returns_clear_message(self):
        response = tool_router.handle_product_request("Show smartphones under ₹10,000")
        self.assertIn("No products were found", response)
        self.assertNotIn("Laptop", response)

    def test_between_price_range_is_inclusive_and_category_aware(self):
        response = tool_router.handle_product_request("Show smartphones between ₹15,000 and ₹22,000")
        self.assertIn("Budget Phone", response)
        self.assertIn("Item-21", response)
        self.assertNotIn("Laptop", response)

    def test_above_price_filter(self):
        response = tool_router.handle_product_request("Show laptops above ₹60,000")
        self.assertIn("Gaming Laptop Pro", response)
        self.assertNotIn("\n- Laptop |", response)

    def test_price_bounds_support_common_customer_formats(self):
        self.assertEqual(
            tool_router._extract_price_bounds("phones under 25k")["upper"], 25000
        )
        self.assertEqual(
            tool_router._extract_price_bounds("phones above 1 lakh")["lower"], 100000
        )
        bounds = tool_router._extract_price_bounds("phones between 20k and 50k")
        self.assertEqual((bounds["lower"], bounds["upper"]), (20000, 50000))

    def test_short_budget_suffix_is_parsed(self):
        self.assertEqual(tool_router._extract_price_limit("under 20k"), 20000)
        self.assertEqual(tool_router._extract_price_limit("below ₹1 lakh"), 100000)


if __name__ == "__main__":
    unittest.main()
