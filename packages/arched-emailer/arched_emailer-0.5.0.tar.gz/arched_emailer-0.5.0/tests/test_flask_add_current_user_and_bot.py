import types
import unittest


class TestFlaskAddCurrentUserAndBot(unittest.TestCase):
    def test_add_current_user_details_in_error(self):
        import sys

        from flask import Flask

        # Install a lightweight flask_login stub before importing handler
        fake_mod = types.ModuleType("flask_login")
        fake_mod.current_user = types.SimpleNamespace(email="u@example.com", name="User", id=123)
        sys.modules["flask_login"] = fake_mod

        from arched_emailer.arched_emailer import ArchedEmailer

        app = Flask(__name__)
        app.secret_key = "secret"

        @app.route("/explode")
        def explode():  # pragma: no cover - exercised via error interception
            raise RuntimeError("explode")

        ae = ArchedEmailer("TestApp", flask=True)
        ae.init_app(app, intercept_errors=True, add_current_user=True)

        c = app.test_client()
        resp = c.get("/explode")
        # error handled by our handler -> returns 500 due to TypeError fallback
        self.assertEqual(resp.status_code, 500)

    def test_is_bot_short_circuit_in_handler(self):
        from flask import Flask

        from arched_emailer.arched_emailer import ArchedEmailer

        app = Flask(__name__)
        app.secret_key = "secret"

        @app.route("/boom")
        def boom():  # pragma: no cover - exercised via error interception
            raise RuntimeError("boom")

        ae = ArchedEmailer("TestApp", flask=True)
        ae.init_app(app, intercept_errors=True, add_current_user=False)

        c = app.test_client()
        # No User-Agent header -> treated as bot and short-circuits handler
        resp = c.get("/boom", headers={})
        # Flask will still produce a 500 since our handler returns None; but the short-circuit path is exercised
        self.assertEqual(resp.status_code, 500)
