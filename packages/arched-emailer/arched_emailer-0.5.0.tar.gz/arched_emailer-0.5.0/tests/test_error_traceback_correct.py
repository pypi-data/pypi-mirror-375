import types


def test_traceback_uses_actual_exception(monkeypatch):
    # Install a capturing SmtpMailer stub directly on the module under test
    from arched_emailer import arched_emailer as mod

    captured = {}

    class CapturingMailer:
        def __init__(self, sender_email, sender_name=None):
            self.sender = types.SimpleNamespace(email=sender_email)

        def send_email(self, recipients, **kwargs):
            captured["recipients"] = recipients
            captured.update(kwargs)

    monkeypatch.setattr(mod, "SmtpMailer", CapturingMailer, raising=True)

    from flask import Flask

    from arched_emailer.arched_emailer import ArchedEmailer

    app = Flask(__name__)
    app.secret_key = "secret"

    @app.route("/boom")
    def boom():  # pragma: no cover - exercised via handler
        raise ValueError("unique-msg-123")

    ae = ArchedEmailer("TestApp", flask=True)
    ae.init_app(app, intercept_errors=True, add_current_user=False)

    c = app.test_client()
    resp = c.get("/boom")
    # Flask will produce a 500; our handler also runs and sends the email via stub
    assert resp.status_code == 500

    # Verify the traceback included references the actual exception raised
    tb = captured.get("traceback", "")
    assert "ValueError" in tb
    assert "unique-msg-123" in tb
    # Also verify we passed exception metadata
    assert captured.get("exception_type") == "ValueError"
    assert "unique-msg-123" in captured.get("exception_message", "")
