import base64
import unittest


class TestSetupAndDecoratorBranch(unittest.TestCase):
    def test_nonflask_setup_and_get_email_path_success_query_and_decorator_db_only_branch(self):
        from arched_emailer.arched_emailer import ArchedEmailer

        # Provide connection string so setup skips API fetch, and initialize SMTP mailers
        kv = "MAIL_HOST=localhost;MAIL_PORT=2525;MAIL_USERNAME=u;MAIL_PASSWORD=p"
        encoded = base64.b64encode(kv.encode()).decode()
        ae = ArchedEmailer("TestApp", api_key="k", mail_connection_string=encoded, flask=False)

        # Exercise _get_email_path success variant and with task query
        # (Will attempt request and log error, but still returns a path)
        p = ae._get_email_path(typ="success", task_id=123)
        self.assertIsInstance(p, str)

        # Decorator branch where send_success=False and send_to_db=True triggers update_db_only path
        @ae.try_log_function(["ops@example.com"], send_success=False, send_to_db=True)
        def ok():
            return {"r": 1}

        self.assertEqual(ok(), {"r": 1})
