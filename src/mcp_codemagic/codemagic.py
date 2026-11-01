"""Thin HTTP client for the Codemagic CI/CD REST API.

Docs: https://docs.codemagic.io/rest-api/overview/

Authentication uses an API token sent in the ``x-auth-token`` header. The token
is read from the ``CODEMAGIC_API_KEY`` environment variable (find it under
Codemagic → Teams / User settings → Integrations → Codemagic API).
"""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlsplit

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


# --- Build logs ---


def _steps(build: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten a build's actions into steps that carry a log URL.

    Script steps keep their log on the first subaction, the built-in steps
    (preparing, fetching, publishing) on the action itself.
    """
    steps = []
    for action in build.get("buildActions") or []:
        log_url = action.get("logUrl")
        status = action.get("status")
        for sub in action.get("subactions") or []:
            log_url = log_url or sub.get("logUrl")
            status = status or sub.get("status")
        steps.append({"name": action.get("name") or "", "status": status, "logUrl": log_url})
    return steps


def pick_step(build: dict[str, Any], step: str | None = None) -> dict[str, Any]:
    """The step whose name contains ``step`` (case-insensitive), or else the
    first failed one, or else the last step that has a log."""
    steps = [s for s in _steps(build) if s["logUrl"]]
    if not steps:
        raise CodemagicError("This build has no step logs yet.")
    if step:
        wanted = step.lower()
        for s in steps:
            if wanted in s["name"].lower():
                return s
        names = ", ".join(s["name"] for s in steps)
        raise CodemagicError(f"No step matching {step!r}. Steps with logs: {names}")
    for s in steps:
        if s["status"] == "failed":
            return s
    return steps[-1]


def get_step_log(log_url: str) -> str:
    """Download one step's log as text.

    The token only goes to the configured Codemagic host, so a log URL that
    points anywhere else is refused rather than sent the credentials.
    """
    if urlsplit(log_url).netloc != urlsplit(_base_url()).netloc:
        raise CodemagicError(f"Refusing to send the API token to {log_url}")
    headers = {**_headers(), "Accept": "text/plain, application/json"}
    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT, follow_redirects=False) as client:
            resp = client.request("GET", log_url, headers=headers)
    except httpx.HTTPError as exc:
        raise CodemagicError(f"Request to {log_url} failed: {exc}") from exc
    if resp.status_code >= 400:
        raise CodemagicError(
            f"Codemagic API {resp.status_code} for GET {log_url}",
            status=resp.status_code,
            body=resp.text[:2000],
        )
    return resp.text


def get_build_log(build_id: str, *, step: str | None = None, tail: int = 200) -> dict[str, Any]:
    """The last ``tail`` lines of one step's log, with the step's name and status."""
    build = get_build(build_id)
    build = build.get("build", build) if isinstance(build, dict) else build
    chosen = pick_step(build, step)
    lines = get_step_log(chosen["logUrl"]).splitlines()
    tail = max(1, tail)
    return {
        "build": build.get("index"),
        "buildStatus": build.get("status"),
        "message": build.get("message"),
        "step": chosen["name"],
        "stepStatus": chosen["status"],
        "lines": len(lines),
        "log": "\n".join(lines[-tail:]),
    }
