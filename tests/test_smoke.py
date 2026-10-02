"""Basic browser-route tests that need no separate testing database."""

import unittest

from app import create_app


class RouteSmokeTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_public_pages_load(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/register").status_code, 200)
        self.assertEqual(self.client.get("/login").status_code, 200)

    def test_private_pages_require_login(self):
        for path in ("/dashboard", "/documents", "/activity", "/admin"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.headers["Location"])


if __name__ == "__main__":
    unittest.main()
