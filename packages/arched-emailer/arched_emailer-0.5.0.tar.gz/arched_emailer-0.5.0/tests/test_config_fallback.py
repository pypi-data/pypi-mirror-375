import base64
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


class TestConfigFallback(unittest.TestCase):
    def setUp(self):
        # Create temp directory and ensure no lingering env
        self.tmpdir = tempfile.mkdtemp(prefix="arched_emailer_test_")
        for k in list(os.environ.keys()):
            if k.startswith("MAIL_"):
                os.environ.pop(k, None)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        for k in list(os.environ.keys()):
            if k.startswith("MAIL_"):
                os.environ.pop(k, None)

    def _write_local_user_details(self, connection_string: str):
        # Mirror where the library saves the file
        path = os.path.join(self.tmpdir, "user_details.json")
        with open(path, "w") as f:
            json.dump({"id": 123, "connection_string": connection_string}, f)

    def test_uses_local_fallback_when_server_down(self):
        # Arrange: base64-encoded connection string
        kv = "MAIL_HOST=smtp.example.com;MAIL_PORT=587;MAIL_USERNAME=user;MAIL_PASSWORD=pass"
        encoded = base64.b64encode(kv.encode()).decode()
        self._write_local_user_details(encoded)

        # Stub third-party dependency not installed in test env
        fake_mod = types.ModuleType("concurrent_log_handler")
        import logging

        class _FakeCRFH(logging.FileHandler):
            def __init__(self, filename, maxBytes=None, backupCount=None):  # noqa: N803
                super().__init__(filename)

        fake_mod.ConcurrentRotatingFileHandler = _FakeCRFH
        sys.modules["concurrent_log_handler"] = fake_mod

        with (
            patch(
                "arched_emailer.arched_emailer.ArchedEmailer._get_create_data_dir",
                return_value=self.tmpdir,
            ),
            patch(
                "arched_emailer.arched_emailer.ArchedEmailer._make_request",
                side_effect=Exception("server down"),
            ),
        ):
            from arched_emailer.arched_emailer import ArchedEmailer

            ae = ArchedEmailer("TestApp", api_key="dummy", mail_connection_string=None)

        # Assert: connection_details sourced from local and env populated
        self.assertEqual(ae.connection_details, encoded)
        self.assertEqual(os.environ.get("MAIL_HOST"), "smtp.example.com")
        self.assertEqual(os.environ.get("MAIL_PORT"), "587")
        self.assertEqual(os.environ.get("MAIL_USERNAME"), "user")
        self.assertEqual(os.environ.get("MAIL_PASSWORD"), "pass")

    def test_no_local_file_and_server_down_keeps_defaults(self):
        # Stub third-party dependency not installed in test env
        fake_mod = types.ModuleType("concurrent_log_handler")
        import logging

        class _FakeCRFH(logging.FileHandler):
            def __init__(self, filename, maxBytes=None, backupCount=None):  # noqa: N803
                super().__init__(filename)

        fake_mod.ConcurrentRotatingFileHandler = _FakeCRFH
        sys.modules["concurrent_log_handler"] = fake_mod

        with (
            patch(
                "arched_emailer.arched_emailer.ArchedEmailer._get_create_data_dir",
                return_value=self.tmpdir,
            ),
            patch(
                "arched_emailer.arched_emailer.ArchedEmailer._make_request",
                side_effect=Exception("server down"),
            ),
        ):
            from arched_emailer.arched_emailer import ArchedEmailer

            ae = ArchedEmailer("TestApp", api_key="dummy", mail_connection_string=None)

        # Assert: no connection details and no MAIL_* envs set
        self.assertIsNone(ae.connection_details)
        self.assertIsNone(os.environ.get("MAIL_HOST"))
        self.assertIsNone(os.environ.get("MAIL_PORT"))
        self.assertIsNone(os.environ.get("MAIL_USERNAME"))
        self.assertIsNone(os.environ.get("MAIL_PASSWORD"))


if __name__ == "__main__":
    unittest.main()
