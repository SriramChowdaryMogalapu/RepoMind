# backend/app/core/security.py
import ipaddress
import re
import socket
from urllib.parse import urlparse

from pydantic import BaseModel


class ParsedGitHubURL(BaseModel):
    owner: str
    repo: str
    full_name: str
    normalized_url: str


GITHUB_URL_REGEX = re.compile(
    r"^(?:https?:\/\/)?(?:www\.)?github\.com\/(?P<owner>[a-zA-Z0-9_\-\.]+)\/(?P<repo>[a-zA-Z0-9_\-\.]+?)(?:\.git)?(?:\/)?$"
)

RESERVED_NAMES = {
    "settings",
    "organizations",
    "orgs",
    "explore",
    "trending",
    "features",
    "topics",
    "collections",
    "events",
    "readme",
    "pricing",
    "site",
    "security",
    "contact",
    "about",
    "login",
    "join",
}

# Regex patterns for common sensitive keys, API tokens, private keys
SECRET_PATTERNS = [
    re.compile(
        r"(?i)(api[_-]?key|secret|token|password|auth|bearer)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?"
    ),
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    re.compile(r"github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}"),
    re.compile(r"sk-[a-zA-Z0-9]{20,48}"),
    re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA )?PRIVATE KEY-----"),
]


def validate_and_parse_github_url(url: str) -> ParsedGitHubURL:
    """
    Validates and normalizes a GitHub repository URL.
    Prevents path traversal, malicious injection, and validates owner/repo format.
    """
    if not url or len(url.strip()) == 0:
        raise ValueError("GitHub URL cannot be empty.")

    clean_url = url.strip()
    match = GITHUB_URL_REGEX.match(clean_url)
    if not match:
        raise ValueError(
            "Invalid GitHub repository URL format. Example: https://github.com/owner/repository"
        )

    owner = match.group("owner")
    repo = match.group("repo")

    # Reject reserved paths or malformed segments
    if owner.lower() in RESERVED_NAMES:
        raise ValueError(
            f"'{owner}' is a reserved GitHub namespace and not a valid repository owner."
        )

    if owner.startswith("-") or owner.endswith("-") or repo.startswith("-") or repo.endswith("-"):
        raise ValueError("Owner and repository names cannot start or end with a hyphen.")

    if ".." in owner or ".." in repo:
        raise ValueError("Invalid characters detected in repository path.")

    full_name = f"{owner.lower()}/{repo.lower()}"
    normalized_url = f"https://github.com/{owner}/{repo}"

    return ParsedGitHubURL(
        owner=owner, repo=repo, full_name=full_name, normalized_url=normalized_url
    )


def redact_secrets(text: str) -> str:
    """
    Redacts discovered API keys, passwords, and tokens from text before returning to clients or logging.
    """
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    return redacted


def is_safe_external_url(url: str) -> bool:
    """
    Validates that a URL is strictly targeted at public GitHub and not an internal network address (SSRF guard).
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False

        hostname = parsed.hostname
        if not hostname or hostname.lower() not in {
            "github.com",
            "raw.githubusercontent.com",
            "api.github.com",
        }:
            return False

        # Resolve hostname and reject private/loopback/link-local IP addresses
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        return not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local)
    except Exception:
        return False
