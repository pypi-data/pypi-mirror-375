import os
import sys
import tempfile
import types
import unittest


def _install_test_stubs():
    # Stub for concurrent_log_handler
    if "concurrent_log_handler" not in sys.modules:
        import logging

        fake_mod = types.ModuleType("concurrent_log_handler")

        class _FakeCRFH(logging.FileHandler):
            def __init__(self, filename, maxBytes=None, backupCount=None):  # noqa: N803
                super().__init__(filename)

        fake_mod.ConcurrentRotatingFileHandler = _FakeCRFH
        sys.modules["concurrent_log_handler"] = fake_mod

    # Stub for smtpymailer
    if "smtpymailer" not in sys.modules:
        fake_mod = types.ModuleType("smtpymailer")

        class FakeSender:
            def __init__(self, email):
                self.email = email

        class SmtpMailer:
            def __init__(self, sender_email, sender_name=None):
                self.sender = FakeSender(sender_email)
                self.message = None

            def send_email(self, *args, **kwargs):  # pragma: no cover
                self.message = types.SimpleNamespace()

        fake_mod.SmtpMailer = SmtpMailer
        sys.modules["smtpymailer"] = fake_mod
 


class TestRedaction(unittest.TestCase):
    def test_redact_text_patterns(self):
        from arched_emailer.encryption import redact_text

        raw = (
            "Contact john.doe@example.com, phone +1-202-555-0199, "
            "card 4111 1111 1111 1111, SSN 123-45-6789, "
            "Authorization: Bearer abcdef.12345-token, password=SuperSecret!"
        )
        red = redact_text(raw)

        self.assertIn("[REDACTED_EMAIL]", red)
        self.assertIn("[REDACTED_PHONE]", red)
        self.assertIn("[REDACTED_CARD]", red)
        self.assertIn("[REDACTED_SSN]", red)
        self.assertIn("Bearer [REDACTED_TOKEN]", red)
        self.assertIn("password=[REDACTED_SECRET]", red)

    def test_obfuscate_sensitive_info_and_value_redaction(self):
        from arched_emailer.encryption import obfuscate_sensitive_info

        data = {
            "api_key": "ABCD-1234-SECRET",
            "user_email": "someone@example.com",
            "notes": "Call at (202) 555-0134",
            "count": 5,
        }

        obf = obfuscate_sensitive_info(data)
        # api_key should be obfuscated with asterisks (not equal to original)
        self.assertNotEqual(obf["api_key"], data["api_key"])
        self.assertIsInstance(obf["api_key"], str)
        self.assertIn("*", obf["api_key"])
        # Values with PII should be redacted even if keys aren't sensitive
        self.assertEqual(obf["user_email"], "[REDACTED_EMAIL]")
        self.assertIn("[REDACTED_PHONE]", obf["notes"])
        # Non-string values pass through
        self.assertEqual(obf["count"], 5)

    def test_logger_redacts_pii(self):
        _install_test_stubs()

        # Defer heavy import until stubs installed
        from unittest.mock import patch

        from arched_emailer.arched_emailer import ArchedEmailer

        tmpdir = tempfile.mkdtemp(prefix="ae_redact_")
        log_path = os.path.join(tmpdir, "ae_redact.log")

        with patch(
            "arched_emailer.arched_emailer.ArchedEmailer._get_create_data_dir",
            return_value=tmpdir,
        ):
            ae = ArchedEmailer("TestApp", flask=True, log_path=log_path)
        ae.log(
            "info",
            "User john.doe@example.com ssn 123-45-6789 pass=myPass token=abc",
        )

        # Ensure content written to the file and redacted
        with open(log_path, "r") as f:
            content = f.read()

        self.assertIn("[REDACTED_EMAIL]", content)
        self.assertIn("[REDACTED_SSN]", content)
        self.assertTrue(
            ("pass=[REDACTED_SECRET]" in content) or ("password=[REDACTED_SECRET]" in content)
        )
