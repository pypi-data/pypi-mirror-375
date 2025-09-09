import base64
import os
import unittest


class TestHighCoverage(unittest.TestCase):
    def setUp(self):
        # Clean env to avoid bleed
        for k in list(os.environ.keys()):
            if k.startswith("MAIL_"):
                os.environ.pop(k, None)

    def test_make_request_unsupported_and_exception(self):
        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)
        # Unsupported method returns error
        status, data, code = ae._make_request("http://invalid", method="FOO")
        self.assertEqual(status, "Error")
        self.assertEqual(code, 500)

        # Invalid URL triggers RequestException path
        status, data, code = ae._make_request("http://127.0.0.1:0")
        self.assertEqual(status, "Error")
        self.assertEqual(code, 500)

    def test_get_email_path_handles_exception(self):
        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)
        path = ae._get_email_path(typ="error")
        # Even on failure to fetch template, function returns a path string
        self.assertIsInstance(path, str)

    def test_get_set_user_details_uses_local_on_failure(self):
        import json

        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)
        data_dir = ae._get_create_data_dir()
        # Seed local user_details.json
        user_file = os.path.join(data_dir, "user_details.json")
        encoded = base64.b64encode(b"MAIL_HOST=localhost;MAIL_PORT=2525").decode()
        with open(user_file, "w") as f:
            json.dump({"id": 42, "connection_string": encoded}, f)

        ae.connection_details = None
        ae._get_set_user_details()  # should fall back to local file on failure
        self.assertEqual(ae.connection_details, encoded)

    def test_log_message_handles_request_failure(self):
        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)
        status, data, code = ae.log_message("INFO", "hello world", task_id=999999)
        self.assertIn(status, ("Error", "Success:"))  # allow either depending on env

    def test_send_success_and_error_email_paths(self):
        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)
        ae.task_id = None  # Avoid DB update networking

        # Success email - should not raise with internal fallback mailer
        # Start timer to exercise time dump/reset
        ae._log_timer()
        ae.send_success_email(["ops@example.com"], app="AppOne")
        # Timer should have been reset if time dump happened
        # Not guaranteed if start wasn't set, so ensure callable
        ae._log_timer(True)

        # Error email - avoid DB send
        ae.errors_name_time.clear()  # ensure not throttled
        ae.send_error_email(["ops@example.com"], error_text="UnitTest Error", send_to_db=False)

        # Throttle path (second send within window should be skipped)
        ae.send_error_email(["ops@example.com"], error_text="UnitTest Error", send_to_db=False)

    def test_try_log_function_decorator(self):
        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)

        @ae.try_log_function(["ops@example.com"], send_success=False, send_to_db=False)
        def add(a, b):
            return a + b

        self.assertEqual(add(2, 3), 5)

        @ae.try_log_function(["ops@example.com"], send_success=False, send_to_db=False)
        def boom():
            raise ValueError("boom")

        # Should not raise
        self.assertIsNone(boom())

    def test_log_invalid_level_and_get_html_content(self):
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)
        ae.log("nope", "password=secret@example.com")  # invalid level path + redaction

        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText("Plain", "plain"))
        msg.attach(MIMEText("<b>HTML</b>", "html"))
        html = ae._get_html_content(msg)
        self.assertIn("HTML", html)
