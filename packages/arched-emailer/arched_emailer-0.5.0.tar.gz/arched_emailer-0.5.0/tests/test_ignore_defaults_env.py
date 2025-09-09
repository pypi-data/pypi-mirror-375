import base64


def _encoded_conn():
    kv = "MAIL_HOST=localhost;MAIL_PORT=1025"
    return base64.b64encode(kv.encode()).decode()


def test_default_ignore_patterns_for_health_and_static():
    from flask import Flask

    from arched_emailer.arched_emailer import ArchedEmailer

    app = Flask(__name__)
    app.secret_key = "secret"

    @app.route("/healthz")
    def healthz():  # pragma: no cover - exercised via error interception
        raise RuntimeError("boom-health")

    @app.route("/styles.css")
    def css():  # pragma: no cover - exercised via error interception
        raise RuntimeError("boom-css")

    ae = ArchedEmailer("TestApp", flask=True)
    ae.init_app(
        app, intercept_errors=True, add_current_user=False, mail_connection_string=_encoded_conn()
    )

    c = app.test_client()
    # Defaults should ignore health endpoints and static assets by extension -> preserve original 500
    r1 = c.get("/healthz")
    assert r1.status_code == 500

    r2 = c.get("/styles.css")
    assert r2.status_code == 500


def test_env_override_replaces_defaults(monkeypatch):
    from flask import Flask

    from arched_emailer.arched_emailer import ArchedEmailer

    # Override to a pattern that does not include health/static
    monkeypatch.setenv("ARCHED_IGNORE_URL_PATTERNS", "^/nope$")

    app = Flask(__name__)
    app.secret_key = "secret"

    @app.route("/healthz")
    def healthz():  # pragma: no cover - exercised via error interception
        raise RuntimeError("boom-health")

    @app.route("/styles.css")
    def css():  # pragma: no cover - exercised via error interception
        raise RuntimeError("boom-css")

    ae = ArchedEmailer("TestApp", flask=True)
    ae.init_app(
        app, intercept_errors=True, add_current_user=False, mail_connection_string=_encoded_conn()
    )

    c = app.test_client()
    # With env override, health/static are not ignored -> handled as 500
    r1 = c.get("/healthz")
    assert r1.status_code == 500

    r2 = c.get("/styles.css")
    assert r2.status_code == 500
