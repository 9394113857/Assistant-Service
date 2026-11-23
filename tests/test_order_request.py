import unittest
from unittest.mock import Mock, patch

from flask import Flask

from app.services import tool_router


class OrderRequestTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.context = self.app.test_request_context(
            "/chat",
            headers={"Authorization": "Bearer test-access-token"},
        )
        self.context.push()
        self.addCleanup(self.context.pop)

    @patch("app.services.tool_router.ORDER_SERVICE_URL", "https://orders.example.com")
    @patch("app.services.tool_router.requests.get")
    def test_fetches_orders_from_current_endpoint_and_forwards_jwt(self, get):
        response = Mock(status_code=200)
        response.json.return_value = {
            "orders": [
                {"order_id": 42, "status": "placed"},
                {"order_id": 41, "status": "shipped"},
            ],
            "pagination": {"page": 1, "size": 10, "total_records": 2},
        }
        get.return_value = response

        result = tool_router.handle_order_request(123)

        get.assert_called_once_with(
            "https://orders.example.com/api/orders/",
            headers={"Authorization": "Bearer test-access-token"},
            timeout=tool_router.PRODUCT_REQUEST_TIMEOUT,
        )
        self.assertIn("Order #42 | Status: placed", result)
        self.assertIn("Order #41 | Status: shipped", result)

    @patch("app.services.tool_router.ORDER_SERVICE_URL", "https://orders.example.com/api/v1/orders/list")
    @patch("app.services.tool_router.requests.get")
    def test_normalizes_legacy_configured_path(self, get):
        response = Mock(status_code=200)
        response.json.return_value = {"orders": [], "pagination": {}}
        get.return_value = response

        result = tool_router.handle_order_request(123)

        self.assertEqual(result, "You have no orders.")
        self.assertEqual(get.call_args.args[0], "https://orders.example.com/api/orders/")

    @patch("app.services.tool_router.ORDER_SERVICE_URL", "https://orders.example.com")
    @patch("app.services.tool_router.requests.get")
    def test_handles_unauthorized_response(self, get):
        get.return_value = Mock(status_code=401)

        self.assertIn("session has expired", tool_router.handle_order_request(123))

    @patch("app.services.tool_router.ORDER_SERVICE_URL", "https://orders.example.com")
    @patch("app.services.tool_router.requests.get")
    def test_handles_unexpected_response_shape(self, get):
        response = Mock(status_code=200)
        response.json.return_value = [{"order_id": 42, "status": "placed"}]
        get.return_value = response

        self.assertIn("unexpected response", tool_router.handle_order_request(123))

    @patch("app.services.tool_router.ORDER_SERVICE_URL", None)
    def test_reports_missing_service_configuration(self):
        self.assertIn("ORDER_SERVICE_URL", tool_router.handle_order_request(123))

    def test_requires_authenticated_user_and_authorization_header(self):
        self.assertIn("login", tool_router.handle_order_request(None))

        with self.app.test_request_context("/chat"):
            self.assertIn("login", tool_router.handle_order_request(123))


if __name__ == "__main__":
    unittest.main()
