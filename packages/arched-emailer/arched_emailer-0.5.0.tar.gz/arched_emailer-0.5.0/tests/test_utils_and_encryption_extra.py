import os
import tempfile
import unittest


class TestUtilsAndEncryptionExtra(unittest.TestCase):
    def test_load_known_bots_from_file_and_isolation(self):
        from arched_emailer.utils import load_known_bots

        tmp = tempfile.mkstemp(prefix="bots_", suffix=".txt")[1]
        with open(tmp, "w") as f:
            f.write("MySpecialBot\n")

        bots = load_known_bots(tmp)
        self.assertIn("myspecialbot", bots)

        # Cleanup
        os.remove(tmp)

    def test_random_and_obfuscation_and_json_secret_redaction(self):
        from arched_emailer.encryption import (
            generate_random_string,
            obfuscate_string,
            redact_text,
        )

        s = generate_random_string(24)
        self.assertEqual(len(s), 24)
        self.assertTrue(all(c.isalnum() for c in s))

        obf = obfuscate_string("abcdefghij")
        self.assertEqual(len(obf), 10)
        self.assertIn("*", obf)

        # JSON-style secret and k=v pattern
        raw_json = '{"password": "abc123", "apiKey": "XYZ"}'
        red = redact_text(raw_json)
        self.assertNotIn("abc123", red)
        self.assertNotIn("XYZ", red)
        self.assertIn("[REDACTED_SECRET]", red)

        kv = "api_key=SECRET_TOKEN"
        self.assertIn("[REDACTED_SECRET]", redact_text(kv))
