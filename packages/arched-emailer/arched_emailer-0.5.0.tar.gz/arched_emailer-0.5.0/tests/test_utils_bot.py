import unittest


class TestUtilsIsBot(unittest.TestCase):
    def test_is_bot_conditions(self):
        from flask import Flask

        from arched_emailer.utils import is_bot

        app = Flask(__name__)

        with app.test_request_context("/", headers={}):
            # No User-Agent -> bot
            self.assertTrue(is_bot())

        with app.test_request_context("/", headers={"User-Agent": "Mozilla"}):
            # Missing Accept -> bot
            self.assertTrue(is_bot())

        with app.test_request_context(
            "/",
            headers={"User-Agent": "Mozilla", "Accept": "text/html"},
        ):
            self.assertFalse(is_bot())

        with app.test_request_context(
            "/",
            headers={"User-Agent": "Googlebot", "Accept": "text/html"},
        ):
            self.assertTrue(is_bot())
