import base64
from contextlib import contextmanager
import os
import sys
import tempfile
import types


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

            def send_email(self, *args, **kwargs):
                # record minimal message-like object
                self.message = types.SimpleNamespace()

        fake_mod.SmtpMailer = SmtpMailer
        sys.modules["smtpymailer"] = fake_mod


@contextmanager
def flask_app():
    from flask import Flask

    app = Flask(__name__)
    app.secret_key = "test-secret"

    @app.route("/boom")
    def boom():  # pragma: no cover - behavior exercised via client
        raise RuntimeError("boom")

    yield app


def _encoded_conn():
    kv = "MAIL_HOST=localhost;MAIL_PORT=1025"
    return base64.b64encode(kv.encode()).decode()


def test_init_app_intercepts_exception_calls_send_error_email(monkeypatch):
    _install_test_stubs()

    from arched_emailer.arched_emailer import ArchedEmailer

    called = {}

    def fake_send_error_email(self, recipients, **kwargs):
        called["recipients"] = recipients
        called["kwargs"] = kwargs

    # Avoid network/template fetch
    monkeypatch.setattr(ArchedEmailer, "send_error_email", fake_send_error_email, raising=True)

    with flask_app() as app:
        ae = ArchedEmailer(
            "TestApp", flask=True, log_path=os.path.join(tempfile.gettempdir(), "ae.log")
        )
        ae.init_app(
            app, intercept_errors=True, api_key="dummy", mail_connection_string=_encoded_conn()
        )

        client = app.test_client()
        resp = client.get("/boom")
        assert resp.status_code == 500
        # Our fake should have been called
        assert called["recipients"] == ["lewis@arched.dev"]


def test_send_error_email_logs_backend(monkeypatch, tmp_path):
    _install_test_stubs()

    from arched_emailer.arched_emailer import ArchedEmailer

    # Capture send_to_db invocations
    recorded = {}

    def fake_send_to_db(self, success=True, **kwargs):
        recorded["success"] = success
        recorded["kwargs"] = kwargs

    monkeypatch.setattr(ArchedEmailer, "_send_to_db", fake_send_to_db, raising=True)

    # Avoid remote template fetch and return a local path
    html_path = tmp_path / "error.html"
    html_path.write_text("<html>Error</html>")
    monkeypatch.setattr(
        ArchedEmailer, "_get_email_path", lambda self, typ="error", task_id=None: str(html_path)
    )

    ae = ArchedEmailer("TestApp", flask=True)
    # Ensure throttling doesn't block our send
    ae.errors_name_time.clear()
    ae.send_error_email(["ops@example.com"], error_text="UnitTestError")

    assert recorded.get("success") is False
    assert recorded["kwargs"].get("recipients") == ["ops@example.com"]
