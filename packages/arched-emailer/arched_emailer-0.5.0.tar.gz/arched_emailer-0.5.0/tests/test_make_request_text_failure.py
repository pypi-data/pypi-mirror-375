from http.server import BaseHTTPRequestHandler, HTTPServer
import threading


class _TextFailHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/textfail":
            self.send_response(503)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"temporary failure")
        else:
            self.send_response(404)
            self.end_headers()


def _server():
    httpd = HTTPServer(("127.0.0.1", 0), _TextFailHandler)
    port = httpd.server_port
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, port


def test_make_request_nonjson_failure_text():
    from arched_emailer.arched_emailer import ArchedEmailer

    httpd, port = _server()
    try:
        ae = ArchedEmailer("TestApp", flask=True)
        status, data, code = ae._make_request(f"http://127.0.0.1:{port}/textfail")
        assert status.startswith("Error")
        assert code == 503
        assert isinstance(data, str) and "temporary failure" in data
    finally:
        httpd.shutdown()
