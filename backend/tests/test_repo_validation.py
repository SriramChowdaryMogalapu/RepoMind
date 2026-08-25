# backend/tests/test_repo_validation.py
import pytest

from app.core.security import validate_and_parse_github_url


def test_valid_github_urls():
    print("\n[TEST] Running validation on valid GitHub URLs...")
    valid_cases = [
        ("https://github.com/octocat/Hello-World", "octocat", "Hello-World", "octocat/hello-world"),
        ("http://github.com/psf/requests.git", "psf", "requests", "psf/requests"),
        ("github.com/fastapi/fastapi/", "fastapi", "fastapi", "fastapi/fastapi"),
    ]
    for url, exp_owner, exp_repo, exp_full_name in valid_cases:
        print(f"[TEST] Testing valid URL: {url}")
        parsed = validate_and_parse_github_url(url)
        assert parsed.owner == exp_owner
        assert parsed.repo == exp_repo
        assert parsed.full_name == exp_full_name
        print(
            f"[TEST] -> Parsed owner='{parsed.owner}', repo='{parsed.repo}', full_name='{parsed.full_name}'"
        )


def test_invalid_github_urls():
    print("\n[TEST] Running validation on invalid / malicious GitHub URLs...")
    invalid_cases = [
        "",
        "https://notgithub.com/user/repo",
        "https://github.com/settings/repo",
        "https://github.com/../traversal",
        "https://github.com/-invalid-/repo",
        "https://github.com/owner",
    ]
    for url in invalid_cases:
        print(f"[TEST] Verifying rejection of malformed URL: '{url}'")
        with pytest.raises(ValueError) as excinfo:
            validate_and_parse_github_url(url)
        print(f"[TEST] -> Correctly caught expected error: {excinfo.value}")
