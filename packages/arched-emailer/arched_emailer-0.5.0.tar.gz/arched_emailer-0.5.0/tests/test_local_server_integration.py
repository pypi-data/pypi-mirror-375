import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import unittest
from urllib.parse import urlparse


class _Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/email/user"):
            payload = {
                "id": 42,
                "connection_string": base64.b64encode(
                    b"MAIL_HOST=localhost;MAIL_PORT=2525;MAIL_USERNAME=u;MAIL_PASSWORD=p"
                ).decode(),
            }
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(payload).encode())
        elif path.startswith("/email/error") or path.startswith("/email/success"):
            # If explicit task=0 query, simulate failure
            if parsed.query == "task=0":
                self._set_headers(404, "text/plain")
                self.wfile.write(b"missing template")
            else:
                self._set_headers(200, "text/html")
                html = "<html><body>TEMPLATE OK</body></html>"
                self.wfile.write(html.encode())
        else:
            self._set_headers(404)
            self.wfile.write(b"not found")

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        # Accept logger and taskrun endpoints
        if path.startswith("/logger/") or path == "/email/tasks/taskrun":
            # Read body for completeness
            length = int(self.headers.get("Content-Length", 0))
            body = b""
            if length:
                body = self.rfile.read(length)

            code = 200
            if path == "/email/tasks/taskrun":
                # If success flag is false in payload, return a 400 to exercise error logging path
                try:
                    data = json.loads(body.decode() or "{}")
                    if not data.get("success", True):
                        code = 400
                except Exception:
                    pass

            # Simulate specific logger failure if path endswith /500
            if path.startswith("/logger/") and path.rstrip("/").endswith("/500"):
                code = 404

            self._set_headers(code, "application/json")
            self.wfile.write(json.dumps({"ok": code == 200}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(b"not found")


def _start_server_in_thread():
    httpd = HTTPServer(("127.0.0.1", 0), _Handler)
    port = httpd.server_port
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, port


class TestLocalServerIntegration(unittest.TestCase):
    def test_integration_against_local_server(self):
        # Spin up local server and point BASE_URL at it
        httpd, port = _start_server_in_thread()
        try:
            import arched_emailer.arched_emailer as mod
            from arched_emailer.arched_emailer import ArchedEmailer

            mod.BASE_URL = f"http://127.0.0.1:{port}"

            # Start without connection_details so _get_set_user_details hits server
            ae = ArchedEmailer("TestApp", flask=True)
            ae.arched_api_key = "k"
            ae.connection_details = None
            ae._get_set_user_details()
            self.assertIsNotNone(ae.connection_details)

            # Fetch and save templates (success + error)
            p_err = ae._get_email_path("error")
            p_suc = ae._get_email_path("success")
            self.assertTrue(p_err and p_suc)

            # Send success email with real send (uses internal fallback mailer) and log to DB
            ae.task_id = 99
            ae._log_timer()
            ae.send_success_email(["ops@example.com"], app="X")

            # Send error email including traceback/env/globals/locals and send_to_db=True
            ae.errors_name_time.clear()
            try:
                raise ValueError("boom")
            except Exception as e:  # noqa: BLE001
                ae.send_error_email(["ops@example.com"], exception=e)

            # Log message (POST)
            status, data, code = ae.log_message("INFO", "hello", task_id=123)
            self.assertTrue(status.startswith("Success"))
            self.assertEqual(code, 200)

            # Simulate logger failure path
            status, data, code = ae.log_message("INFO", "hello", task_id=500)
            self.assertTrue(status.startswith("Error"))
            self.assertEqual(code, 404)

            # Exercise template fetch failure via task=0
            _ = ae._get_email_path("error", task_id=0)
        finally:
            httpd.shutdown()
