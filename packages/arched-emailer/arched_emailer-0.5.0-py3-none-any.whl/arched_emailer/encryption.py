import random
import re
import secrets
import string
from typing import Any


def generate_random_string(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


def obfuscate_string(s: str) -> str:
    """
    Obfuscates a string by replacing 50% of its characters with asterisks
    Args:
        s (str): The string to obfuscate

    Returns:
        str: The obfuscated string
    """
    # Convert the string to a list of characters to facilitate replacements
    chars = list(s)
    # Determine the indices to replace with asterisks, selecting 50% of the characters at random
    indices_to_obfuscate = random.sample(range(len(chars)), k=len(chars) // 2)
    # Replace the selected characters with asterisks
    for index in indices_to_obfuscate:
        chars[index] = "*"
    # Convert the list of characters back to a string
    return "".join(chars)


def obfuscate_sensitive_info(data: dict[str, Any]) -> dict[str, Any]:
    """
    Obfuscate sensitive information in a dictionary, such as API keys and passwords.
    Args:
        data (dict): The dictionary to obfuscate

    Returns:
        dict: The obfuscated dictionary
    """
    copy_data = data.copy()

    sensitive_keywords = [
        "api_key",
        "apikey",
        "password",
        "passwd",
        "pwd",
        "_key",
        "secret",
        "token",
        "database_url",
    ]
    obfuscated_data = {}
    for k, v in copy_data.items():
        if "__" not in k and "sys" not in k:
            # Check if the key, in lowercase, contains any of the sensitive keywords
            if any(keyword in k.lower() for keyword in sensitive_keywords) and isinstance(v, str):
                # Obfuscate the value if the key is considered sensitive
                obfuscated_data[k] = obfuscate_string(str(v))
            else:
                # Redact PII in any string values even if key isn't explicitly sensitive
                if isinstance(v, str):
                    obfuscated_data[k] = redact_text(v)
                else:
                    # Keep the original value if not a string
                    obfuscated_data[k] = v
    return obfuscated_data


def redact_text(text: str) -> str:
    """
    Redact common PII and secrets in free-form text deterministically.

    The following items are redacted:
    - Email addresses -> [REDACTED_EMAIL]
    - Phone numbers -> [REDACTED_PHONE]
    - Credit card-like numbers -> [REDACTED_CARD]
    - US SSN patterns -> [REDACTED_SSN]
    - Bearer tokens -> Bearer [REDACTED_TOKEN]
    - Inline secrets for keys like password/apiKey/token/secret in both JSON and k=v forms
    """
    if not text:
        return text

    redacted = text

    # Emails
    email_regex = re.compile(r"([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
    redacted = email_regex.sub("[REDACTED_EMAIL]", redacted)

    # Phone numbers (basic international/US patterns)
    phone_regex = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}\b")
    redacted = phone_regex.sub("[REDACTED_PHONE]", redacted)

    # Credit cards (13-19 digits, allowing spaces or dashes)
    cc_regex = re.compile(r"\b(?:\d[ \-]?){13,19}\b")
    redacted = cc_regex.sub("[REDACTED_CARD]", redacted)

    # US SSN
    ssn_regex = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    redacted = ssn_regex.sub("[REDACTED_SSN]", redacted)

    # Bearer tokens
    bearer_regex = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-~+/=]+")
    redacted = bearer_regex.sub("Bearer [REDACTED_TOKEN]", redacted)

    # JSON-style secrets: "password": "value", "apiKey": "value", etc.
    json_secret_regex = re.compile(
        r"(?i)(\"?(?:password|pass|passwd|pwd|api[_-]?key|token|secret)\"?\s*:\s*)(\"?)([^\"\s,}]+)(\"?)"
    )
    redacted = json_secret_regex.sub(r"\1[REDACTED_SECRET]", redacted)

    # k=v style secrets: password=value, api_key=value, token=value
    kv_secret_regex = re.compile(
        r"(?i)\b(password|pass|passwd|pwd|api[_-]?key|token|secret)\s*[:=]\s*([^\s,;]+)"
    )
    redacted = kv_secret_regex.sub(lambda m: f"{m.group(1)}=[REDACTED_SECRET]", redacted)

    return redacted
