# backend/tests/test_security.py
from app.core.rate_limiter import InMemoryRateLimiter
from app.core.security import is_safe_external_url, redact_secrets


def test_secret_redaction():
    print("\n[TEST] Verifying secret & token redaction rules...")
    sample_text = (
        "Authorization: Bearer sk-1234567890abcdef1234567890\n"
        "GITHUB_TOKEN = 'ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'\n"
        "password = 'my_super_secret_password_123'\n"
        "Normal code line: return user.is_active"
    )

    redacted = redact_secrets(sample_text)
    print(f"[TEST] Redacted output:\n{redacted}")

    assert "ghp_" not in redacted
    assert "sk-" not in redacted
    assert "my_super_secret_password_123" not in redacted
    assert "[REDACTED_SECRET]" in redacted
    assert "Normal code line: return user.is_active" in redacted
    print("[TEST] Sensitive tokens scrubbed successfully.")


def test_ssrf_url_guard():
    print("\n[TEST] Verifying SSRF protection and external URL filtering...")
    safe_urls = [
        "https://github.com/octocat/Hello-World",
        "https://raw.githubusercontent.com/octocat/Hello-World/main/README.md",
        "https://api.github.com/repos/octocat/Hello-World",
    ]
    for url in safe_urls:
        allowed = is_safe_external_url(url)
        print(f"[TEST] Checking safe URL '{url}' -> Allowed: {allowed}")
        assert allowed is True

    unsafe_urls = [
        "http://169.254.169.254/latest/meta-data/",  # AWS metadata endpoint
        "http://127.0.0.1:5432",  # Local database
        "http://localhost:8000",
        "https://attacker.com/malicious",
        "file:///etc/passwd",
    ]
    for url in unsafe_urls:
        allowed = is_safe_external_url(url)
        print(f"[TEST] Checking SSRF/unsafe URL '{url}' -> Allowed: {allowed}")
        assert allowed is False
    print("[TEST] SSRF validation blocked internal and unauthorized hosts.")


def test_rate_limiter():
    print("\n[TEST] Verifying sliding window rate limiter...")
    limiter = InMemoryRateLimiter(requests_per_minute=3)
    client_ip = "192.168.1.50"

    assert limiter.is_allowed(client_ip) is True
    assert limiter.is_allowed(client_ip) is True
    assert limiter.is_allowed(client_ip) is True
    # 4th request must be rejected
    assert limiter.is_allowed(client_ip) is False
    print("[TEST] Rate limit cap of 3 requests per minute enforced correctly.")
