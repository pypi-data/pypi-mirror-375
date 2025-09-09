import os
import tempfile
import unittest


class TestFlaskIgnoreAndTemplates(unittest.TestCase):
    def test_flask_ignore_patterns_and_custom_templates(self):
        from flask import Flask

        from arched_emailer.arched_emailer import ArchedEmailer

        # Create a temporary template folder with simple templates
        tmpdir = tempfile.mkdtemp(prefix="ae_tmpl_")
        other_tmpl = os.path.join(tmpdir, "other.html")
        not_found_tmpl = os.path.join(tmpdir, "404.html")
        with open(other_tmpl, "w") as f:
            f.write("<html><body>OTHER TEMPLATE</body></html>")
        with open(not_found_tmpl, "w") as f:
            f.write("<html><body>NOT FOUND</body></html>")

        app = Flask(__name__, template_folder=tmpdir)
        app.secret_key = "test-secret"

        # One valid route to populate visited_urls via before_request
        @app.route("/alive")
        def alive():  # pragma: no cover - endpoint body not relevant
            return "ok"

        ae = ArchedEmailer("TestApp", flask=True)
        ae.init_app(
            app,
            intercept_errors=True,
            add_current_user=False,  # avoid flask_login dependency in tests
            ignore_url_patterns=[r"^/health$"],
            error_templates={404: "404.html", "other": "other.html"},
        )

        client = app.test_client()

        # Hit a real route a few times to exercise before_request visited_urls tracking
        for _ in range(2):
            self.assertEqual(client.get("/alive").status_code, 200)

        # 1) Missing route that matches ignore pattern -> returns 404 template with original 404
        r1 = client.get("/health")
        self.assertEqual(r1.status_code, 404)
        self.assertIn(b"NOT FOUND", r1.data)

        # 2) Missing route that does not match ignore pattern -> preserved 404
        r2 = client.get("/missing")
        self.assertEqual(r2.status_code, 404)
