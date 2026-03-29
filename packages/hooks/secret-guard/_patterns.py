"""Secret detection patterns and utilities for secret-guard."""
import re
from math import log2


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {c: s.count(c) / len(s) for c in set(s)}
    return -sum(p * log2(p) for p in freq.values())


# Secret patterns: id, regex (compiled), secret_group (capture group for entropy), entropy_threshold (optional)
SECRET_PATTERNS = [
    {
        "id": "aws-access-key",
        "regex": re.compile(r'AKIA[0-9A-Z]{16}'),
        "secret_group": None,
        "entropy_threshold": None,
        "message": "AWS access key detected",
    },
    {
        "id": "generic-api-key",
        "regex": re.compile(r'\b[A-Za-z_]*(SECRET|PASSWORD|TOKEN|API_KEY)[A-Za-z_0-9]*\s*=\s*(\S{8,})', re.IGNORECASE),
        "secret_group": 2,
        "entropy_threshold": 3.5,
        "message": "High-entropy API key/secret detected",
    },
    {
        "id": "private-key-pem",
        "regex": re.compile(r'-----BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY-----'),
        "secret_group": None,
        "entropy_threshold": None,
        "message": "Private key detected",
    },
    {
        "id": "github-token",
        "regex": re.compile(r'gh[pousr]_[A-Za-z0-9]{36}'),
        "secret_group": None,
        "entropy_threshold": None,
        "message": "GitHub personal access token detected",
    },
    {
        "id": "stripe-live-key",
        "regex": re.compile(r'sk_live_[0-9a-zA-Z]{24,}'),
        "secret_group": None,
        "entropy_threshold": None,
        "message": "Stripe live secret key detected",
    },
]

# Exfiltration patterns for Bash commands
EXFIL_PATTERNS = [
    {"id": "source-env",    "regex": re.compile(r'(source|\.)\s+[^\s;|&]*\.env\b'),       "message": "Sourcing .env file blocked"},
    {"id": "base64-secret", "regex": re.compile(r'\bbase64\b[^|;]*(\.env|credentials|id_rsa|\.pem)'), "message": "Base64 encoding of secrets blocked"},
    {"id": "nc-secret",     "regex": re.compile(r'\bnc\b[^;|&]*<[^;|&]*(\.env|credentials|id_rsa)'),  "message": "Netcat exfiltration of secrets blocked"},
    {"id": "proc-environ",  "regex": re.compile(r'/proc/[0-9]+/environ'),                  "message": "Process environment read blocked"},
    {"id": "scp-secret",    "regex": re.compile(r'\bscp\b[^;|&]*(\.env|credentials|id_rsa)\b[^;|&]*:'), "message": "SCP exfiltration of secrets blocked"},
]

# .env.example allowlist — these file paths are never blocked
ENV_EXAMPLE_PATTERNS = [
    re.compile(r'\.env\.(example|sample|template|schema|defaults)$', re.IGNORECASE),
    re.compile(r'(example|sample|template)\.env$', re.IGNORECASE),
    re.compile(r'env\.(example|sample|template)$', re.IGNORECASE),
]


def is_env_example(file_path: str) -> bool:
    return any(p.search(file_path) for p in ENV_EXAMPLE_PATTERNS)


def scan_for_secrets(text: str) -> tuple:
    """Returns (found: bool, message: str)"""
    for pattern in SECRET_PATTERNS:
        m = pattern["regex"].search(text)
        if not m:
            continue
        if pattern["secret_group"] is not None and pattern["entropy_threshold"] is not None:
            value = m.group(pattern["secret_group"])
            if shannon_entropy(value) < pattern["entropy_threshold"]:
                continue
        return True, pattern["message"]
    return False, ""


def scan_for_exfil(command: str) -> tuple:
    """Returns (found: bool, message: str)"""
    for pattern in EXFIL_PATTERNS:
        if pattern["regex"].search(command):
            return True, pattern["message"]
    return False, ""


