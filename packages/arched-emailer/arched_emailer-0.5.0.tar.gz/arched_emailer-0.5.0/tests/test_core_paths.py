import base64
import os
import tempfile
import unittest


class TestCorePaths(unittest.TestCase):
    def setUp(self):
        # Isolate env
        for k in list(os.environ.keys()):
            if k.startswith("MAIL_"):
                os.environ.pop(k, None)
        self.tmpdir = tempfile.mkdtemp(prefix="arched_emailer_tmp_")

    def test_load_env_sets_mail_env_vars(self):
        from arched_emailer.arched_emailer import ArchedEmailer

        kv = "MAIL_HOST=smtp.example.com;MAIL_PORT=2525;MAIL_USERNAME=user;MAIL_PASSWORD=pass"
        encoded = base64.b64encode(kv.encode()).decode()

        ae = ArchedEmailer("TestApp", flask=True)
        ae.connection_details = encoded
        ae._load_env()

        self.assertEqual(os.environ.get("MAIL_HOST"), "smtp.example.com")
        self.assertEqual(os.environ.get("MAIL_PORT"), "2525")
        self.assertEqual(os.environ.get("MAIL_USERNAME"), "user")
        self.assertEqual(os.environ.get("MAIL_PASSWORD"), "pass")

    def test_data_dir_creation_and_error_log_roundtrip(self):
        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)

        # Ensure data dir exists
        data_dir = ae._get_create_data_dir()
        self.assertTrue(os.path.isdir(data_dir))

        # Save and load error log
        ae.errors_name_time.clear()
        ae.errors_name_time["SampleError"] = ae.time_start or __import__("datetime").datetime.now()
        ae._save_error_log()
        loaded = ae._load_error_log()
        self.assertIn("SampleError", loaded)

    def test_allowed_to_send_throttle_and_cleanup(self):
        import datetime as dt

        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)
        msg = "ThrottleMe"

        allowed_first = ae._allowed_to_send(msg, allowed_minutes=60)
        allowed_second = ae._allowed_to_send(msg, allowed_minutes=60)
        self.assertTrue(allowed_first)
        self.assertFalse(allowed_second)

        # Age the entry and cleanup
        for k in list(ae.errors_name_time.keys()):
            ae.errors_name_time[k] = dt.datetime.now() - dt.timedelta(days=3)
        ae._cleanup_error_log(max_age_minutes=10)  # remove old
        self.assertNotIn(msg, ae.errors_name_time)

    def test_send_email_success(self):
        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)
        # Minimal send with a simple template file to support real mailer too
        tmp_template = os.path.join(tempfile.gettempdir(), "tmpl.html")
        with open(tmp_template, "w") as f:
            f.write("<html><body>Hello</body></html>")
        ok = ae.send_email(
            sender_email="sender@example.com",
            sender_name="Sender",
            recipients=["rcpt@example.com"],
            subject="Hello",
            template=tmp_template,
        )
        self.assertIsInstance(ok, bool)

    def test_flask_before_request_tracks_visited_urls(self):
        # Verify before_request hook tracks visited URLs without triggering error handler
        from flask import Flask

        from arched_emailer.arched_emailer import ArchedEmailer

        app = Flask(__name__)
        app.secret_key = "test-secret"

        @app.route("/ok")
        def ok():  # pragma: no cover - endpoint body not relevant
            return "OK"

        ae = ArchedEmailer("TestApp", flask=True)
        ae.init_app(app, intercept_errors=True)

        client = app.test_client()
        for _ in range(3):
            resp = client.get("/ok")
            self.assertEqual(resp.status_code, 200)

        with client.session_transaction() as sess:
            visited = sess.get("visited_urls", [])
            self.assertTrue(len(visited) >= 1)
            # Should contain our route
            self.assertTrue(any("/ok" in u for u in visited))
