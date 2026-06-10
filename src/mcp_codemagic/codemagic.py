"""Thin HTTP client for the Codemagic CI/CD REST API.

Docs: https://docs.codemagic.io/rest-api/overview/

Authentication uses an API token sent in the ``x-auth-token`` header. The token
is read from the ``CODEMAGIC_API_KEY`` environment variable (find it under
Codemagic → Teams / User settings → Integrations → Codemagic API).
"""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://api.codemagic.io"
DEFAULT_TIMEOUT = 30.0
TOKEN_ENV = "CODEMAGIC_API_KEY"


class CodemagicError(RuntimeError):
    """Raised when the Codemagic API returns a non-2xx response or is misconfigured."""

    def __init__(self, message: str, *, status: int | None = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


def _token() -> str:
    token = os.getenv(TOKEN_ENV)
    if not token:
        raise CodemagicError(
            f"Missing {TOKEN_ENV}. Set it in your environment or .env file "
            "(Codemagic → User/Team settings → Integrations → Codemagic API)."
        )
    return token


def _base_url() -> str:
    return os.getenv("CODEMAGIC_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _headers() -> dict[str, str]:
    return {
        "x-auth-token": _token(),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "mcp-codemagic (+https://github.com/musictechlab/mcp-codemagic)",
    }


def _request(method: str, path: str, **kwargs: Any) -> Any:
    url = f"{_base_url()}{path}"
    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
            resp = client.request(method, url, headers=_headers(), **kwargs)
    except httpx.HTTPError as exc:
        raise CodemagicError(f"Request to {url} failed: {exc}") from exc

    if resp.status_code >= 400:
        try:
            body = resp.json()
        except ValueError:
            body = resp.text
        raise CodemagicError(
            f"Codemagic API {resp.status_code} for {method} {path}",
            status=resp.status_code,
            body=body,
        )

    if not resp.content:
        return None
    try:
        return resp.json()
    except ValueError:
        return resp.text


# --- Applications ---


def list_apps() -> Any:
    """List all applications available to the API token."""
    return _request("GET", "/apps")


def get_app(app_id: str) -> Any:
    """Get a single application by its id."""
    return _request("GET", f"/apps/{app_id}")


# --- Builds ---


def start_build(
    app_id: str,
    workflow_id: str,
    *,
    branch: str | None = None,
    tag: str | None = None,
    environment: dict[str, Any] | None = None,
    labels: list[str] | None = None,
) -> Any:
    """Trigger a build for an app/workflow on a branch or tag.

    Exactly one of ``branch`` or ``tag`` should be provided.
    """
    if bool(branch) == bool(tag):
        raise CodemagicError("Provide exactly one of 'branch' or 'tag'.")

    payload: dict[str, Any] = {"appId": app_id, "workflowId": workflow_id}
    if branch:
        payload["branch"] = branch
    if tag:
        payload["tag"] = tag
    if environment:
        payload["environment"] = environment
    if labels:
        payload["labels"] = labels
    return _request("POST", "/builds", json=payload)


def get_build(build_id: str) -> Any:
    """Get the status and details of a single build."""
    return _request("GET", f"/builds/{build_id}")


def list_builds(
    *,
    app_id: str | None = None,
    workflow_id: str | None = None,
    branch: str | None = None,
    status: str | None = None,
) -> Any:
    """List builds, optionally filtered by app, workflow, branch, or status."""
    params: dict[str, str] = {}
    if app_id:
        params["appId"] = app_id
    if workflow_id:
        params["workflowId"] = workflow_id
    if branch:
        params["branch"] = branch
    if status:
        params["status"] = status
    return _request("GET", "/builds", params=params or None)


def cancel_build(build_id: str) -> Any:
    """Cancel a running or queued build."""
    return _request("POST", f"/builds/{build_id}/cancel")
