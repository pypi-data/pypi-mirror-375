import base64
import json
import os
import unittest


class TestMorePaths(unittest.TestCase):
    def test_process_error_with_json_form_xml_and_direct_send(self):
        from flask import Flask

        from arched_emailer.arched_emailer import ArchedEmailer

        app = Flask(__name__)
        app.secret_key = "secret"

        @app.route("/boom", methods=["GET", "POST"])
        def boom():  # pragma: no cover - exercised via error interception
            raise RuntimeError("boom")

        ae = ArchedEmailer("TestApp", flask=True)
        ae.init_app(app, intercept_errors=True, add_current_user=False)

        c = app.test_client()

        # JSON body
        rj = c.post("/boom", json={"a": 1, "b": 2})
        self.assertEqual(rj.status_code, 500)

        # Form body
        rf = c.post("/boom", data={"x": "1", "y": "2"})
        self.assertEqual(rf.status_code, 500)

        # XML body
        rx = c.post("/boom", data="<a>1</a>", content_type="application/xml")
        self.assertEqual(rx.status_code, 500)

        # Direct send_error_email to exercise globals/locals/env dumping and allowed_to_send
        ae.errors_name_time.clear()
        ae.send_error_email(
            ["ops@example.com"], error_text="UniqueErrorForCoverage", send_to_db=False
        )

    def test_make_request_all_methods_and_logger_fallback_and_user_details_local_errors(self):
        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)

        # Exercise all method branches with invalid endpoint to trigger exception handling
        for method in ("GET", "POST", "PUT", "DELETE"):
            status, data, code = ae._make_request("http://127.0.0.1:0", method=method)
            self.assertEqual(status, "Error")
            self.assertEqual(code, 500)

        # Logger fallback path when logger is None
        ae.logger = None
        ae.log("info", "this should go to stderr without raising")

        # Local user details - bad JSON to trigger exception handling
        data_dir = ae._get_create_data_dir()
        bad_file = os.path.join(data_dir, "user_details.json")
        with open(bad_file, "w") as f:
            f.write("{not json}")
        ae.connection_details = None
        ae._load_user_details_from_local()  # should handle json error gracefully

        # Now good JSON to ensure field assignment path
        encoded = base64.b64encode(b"MAIL_HOST=localhost;MAIL_PORT=2525").decode()
        with open(bad_file, "w") as f:
            json.dump({"id": 7, "connection_string": encoded}, f)
        ae._load_user_details_from_local()
        self.assertEqual(ae.connection_details, encoded)
