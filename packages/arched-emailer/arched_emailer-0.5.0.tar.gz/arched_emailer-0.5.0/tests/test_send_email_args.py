import os
import tempfile


def test_send_email_with_cc_bcc_and_template_path():
    from arched_emailer.arched_emailer import ArchedEmailer

    ae = ArchedEmailer("TestApp", flask=True)
    # provide a small HTML template file
    tmp_template = os.path.join(tempfile.gettempdir(), "tmpl_send.html")
    with open(tmp_template, "w") as f:
        f.write("<html><body>Hi</body></html>")

    ok = ae.send_email(
        sender_email="s@example.com",
        sender_name="Sender",
        recipients=["r@example.com"],
        subject="Test",
        cc_recipients=["c@example.com"],
        bcc_recipients=["b@example.com"],
        template=tmp_template,
    )
    assert isinstance(ok, bool)
