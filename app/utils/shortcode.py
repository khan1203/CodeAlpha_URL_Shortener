"""
Utility for generating short, URL-safe random codes.

Uses `secrets` (not `random`) because it is cryptographically secure and
unpredictable, which matters even for a "simple" URL shortener - predictable
codes let people guess/enumerate other users' shortened links.
"""

import secrets
import string

_ALPHABET = string.ascii_letters + string.digits  # a-zA-Z0-9


def generate_short_code(length: int = 6) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))
