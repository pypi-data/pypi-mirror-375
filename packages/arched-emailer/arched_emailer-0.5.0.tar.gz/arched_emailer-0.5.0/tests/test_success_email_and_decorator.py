import unittest


class TestSuccessEmailAndDecorator(unittest.TestCase):
    def test_try_log_function_with_success_email(self):
        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)

        @ae.try_log_function(
            ["ops@example.com"],
            send_success=True,
            success_recipients=["ops@example.com"],
            send_to_db=False,
        )
        def concat(a, b):
            return f"{a}-{b}"

        result = concat("x", "y")
        self.assertEqual(result, "x-y")

    def test_send_success_email_update_db_only_and_plain_only_html_extract(self):
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)

        # Exercise update_db_only flag and timer dump/reset path
        ae._log_timer()
        ae.send_success_email(
            ["ops@example.com"],
            app="MyApp",
            update_db_only=True,  # skip actual send but still exercise DB logging path (no task_id => no network)
            extra="value",
        )
        ae._log_timer(True)

        # Extract HTML content when message has no HTML part -> empty string
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText("only text", "plain"))
        html = ae._get_html_content(msg)
        self.assertEqual(html, "")
