"""Unit tests for the Codemagic client and MCP tools.

Network is never touched — httpx requests are monkeypatched.
"""

from __future__ import annotations

import json

import pytest

from mcp_codemagic import codemagic, server


class FakeResponse:
    def __init__(self, status_code: int, payload=None, *, text: str = ""):
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.content = b"x" if payload is not None or text else b""

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


class FakeClient:
    """Stand-in for httpx.Client that records the last request and returns a canned response."""

    last_request: dict | None = None

    def __init__(self, response: FakeResponse):
        self._response = response

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def request(self, method, url, headers=None, **kwargs):
        FakeClient.last_request = {
            "method": method,
            "url": url,
            "headers": headers,
            **kwargs,
        }
        return self._response


@pytest.fixture(autouse=True)
def _token(monkeypatch):
    monkeypatch.setenv("CODEMAGIC_API_KEY", "test-token")


def _patch_client(monkeypatch, response: FakeResponse):
    FakeClient.last_request = None
    monkeypatch.setattr(codemagic.httpx, "Client", lambda *a, **k: FakeClient(response))


def test_missing_token_raises(monkeypatch):
    monkeypatch.delenv("CODEMAGIC_API_KEY", raising=False)
    with pytest.raises(codemagic.CodemagicError, match="Missing CODEMAGIC_API_KEY"):
        codemagic.list_apps()


def test_list_apps_sends_auth_header(monkeypatch):
    _patch_client(monkeypatch, FakeResponse(200, {"applications": []}))
    result = codemagic.list_apps()
    assert result == {"applications": []}
    req = FakeClient.last_request
    assert req["url"].endswith("/apps")
    assert req["headers"]["x-auth-token"] == "test-token"


def test_start_build_requires_branch_xor_tag(monkeypatch):
    _patch_client(monkeypatch, FakeResponse(200, {"buildId": "abc"}))
    with pytest.raises(codemagic.CodemagicError, match="exactly one"):
        codemagic.start_build("app1", "wf1")
    with pytest.raises(codemagic.CodemagicError, match="exactly one"):
        codemagic.start_build("app1", "wf1", branch="main", tag="v1")


def test_start_build_payload(monkeypatch):
    _patch_client(monkeypatch, FakeResponse(200, {"buildId": "abc"}))
    codemagic.start_build("app1", "ios-release", branch="main")
    body = FakeClient.last_request["json"]
    assert body == {"appId": "app1", "workflowId": "ios-release", "branch": "main"}


def test_error_status_raises_with_body(monkeypatch):
    _patch_client(monkeypatch, FakeResponse(404, {"message": "not found"}))
    with pytest.raises(codemagic.CodemagicError) as exc:
        codemagic.get_build("missing")
    assert exc.value.status == 404
    assert exc.value.body == {"message": "not found"}


def test_server_tool_wraps_errors_as_json(monkeypatch):
    monkeypatch.delenv("CODEMAGIC_API_KEY", raising=False)
    out = server.codemagic_list_apps()
    parsed = json.loads(out)
    assert "Missing CODEMAGIC_API_KEY" in parsed["error"]


def test_server_tool_returns_pretty_json(monkeypatch):
    _patch_client(monkeypatch, FakeResponse(200, {"build": {"status": "building"}}))
    out = server.codemagic_get_build("abc")
    assert json.loads(out) == {"build": {"status": "building"}}
