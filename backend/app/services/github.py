# backend/app/services/github.py
from typing import Any

import httpx
from fastapi import status

from app.core.config import settings
from app.core.errors import AppException


class GitHubClient:
    def __init__(self, token: str | None = None):
        self.token = token or settings.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "RepoMind-App"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    async def get_repository_metadata(self, owner: str, repo: str) -> dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=self.headers)
            if resp.status_code == 404:
                raise AppException(
                    code="REPO_NOT_FOUND",
                    message=f"Repository '{owner}/{repo}' was not found or is private.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            if resp.status_code == 403:
                raise AppException(
                    code="GITHUB_RATE_LIMITED",
                    message="GitHub API rate limit exceeded. Please configure a GITHUB_TOKEN.",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            if resp.status_code != 200:
                raise AppException(
                    code="GITHUB_API_ERROR",
                    message=f"GitHub API error: {resp.text}",
                    status_code=status.HTTP_502_BAD_GATEWAY,
                )
            return resp.json()

    async def get_file_tree(
        self, owner: str, repo: str, default_branch: str
    ) -> list[dict[str, Any]]:
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self.headers)
            if resp.status_code != 200:
                raise AppException(
                    code="TREE_FETCH_FAILED",
                    message=f"Failed to fetch repository file tree for branch '{default_branch}'.",
                    status_code=status.HTTP_502_BAD_GATEWAY,
                )
            data = resp.json()
            return data.get("tree", [])

    async def fetch_file_content(
        self, owner: str, repo: str, path: str, default_branch: str
    ) -> str | None:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{path}"
        headers = {}
        if self.token:
            headers["Authorization"] = f"token {self.token}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(raw_url, headers=headers)
            if resp.status_code == 200:
                return resp.text
            return None
