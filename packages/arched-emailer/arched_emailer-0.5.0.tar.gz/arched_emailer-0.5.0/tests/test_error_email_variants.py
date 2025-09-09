import unittest


class TestErrorEmailVariants(unittest.TestCase):
    def test_send_error_email_variants_and_sender_override(self):
        from arched_emailer.arched_emailer import ArchedEmailer

        ae = ArchedEmailer("TestApp", flask=True)

        # Ensure throttling does not block
        ae.errors_name_time.clear()

        # Minimal send with all dumps disabled and explicit sender override
        ae.send_error_email(
            "ops@example.com",  # accept str as recipients
            error_text="VariantOne",
            include_tb=False,
            dump_enviro=False,
            dump_globals=False,
            dump_locals=False,
            sender="alerts@example.com",
            sender_name="Alerts",
            send_to_db=False,
        )

        # With allowed_minutes=0, repeated sends should be allowed immediately
        ae.send_error_email(
            ["ops@example.com"],
            error_text="VariantOne",
            include_tb=False,
            dump_enviro=False,
            dump_globals=False,
            dump_locals=False,
            allowed_minutes=0,
            send_to_db=False,
        )
