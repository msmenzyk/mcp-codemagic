"""Codemagic MCP server — trigger and inspect CI/CD builds from Claude Code."""

from __future__ import annotations

import json
from functools import wraps

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from . import codemagic
from .codemagic import CodemagicError

load_dotenv()

mcp = FastMCP(
    "codemagic",
    instructions=(
        "Codemagic CI/CD integration. List applications and their workflows, "
        "trigger builds on a branch or tag, check build status, list recent "
        "builds, read the log of a build step, and cancel running builds. Requires the CODEMAGIC_API_KEY "
        "environment variable (Codemagic → Integrations → Codemagic API)."
    ),
)


def _ok(payload) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _safe(func):
    """Return Codemagic errors as readable JSON instead of raising.

    functools.wraps preserves the signature so FastMCP can build the tool schema.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CodemagicError as exc:
            return json.dumps(
                {"error": str(exc), "status": exc.status, "body": exc.body},
                ensure_ascii=False,
            )

    return wrapper


@mcp.tool()
@_safe
def codemagic_list_apps() -> str:
    """List all applications connected to your Codemagic account.

    Returns each application's id, name, connected repository, and the
    workflow ids defined in its codemagic.yaml. Use the app id and a workflow
    id with codemagic_start_build to trigger a build.
    """
    return _ok(codemagic.list_apps())


@mcp.tool()
@_safe
def codemagic_get_app(app_id: str) -> str:
    """Get details for a single Codemagic application.

    Returns the app's repository, branches, workflows, and recent build
    references.

    Args:
        app_id: The Codemagic application id (from codemagic_list_apps).
    """
    return _ok(codemagic.get_app(app_id))


@mcp.tool()
@_safe
def codemagic_start_build(
    app_id: str,
    workflow_id: str,
    branch: str | None = None,
    tag: str | None = None,
) -> str:
    """Trigger a new build for an app/workflow on a branch or tag.

    Provide exactly one of branch or tag. Returns the new buildId, which you
    can poll with codemagic_get_build.

    Args:
        app_id: The Codemagic application id.
        workflow_id: The workflow id from codemagic.yaml (e.g. "ios-release").
        branch: Branch to build (e.g. "main"). Mutually exclusive with tag.
        tag: Git tag to build (e.g. "v1.2.0"). Mutually exclusive with branch.
    """
    return _ok(codemagic.start_build(app_id, workflow_id, branch=branch, tag=tag))


@mcp.tool()
@_safe
def codemagic_get_build(build_id: str) -> str:
    """Get the status and details of a single build.

    Status values include "queued", "building", "finishing", "publishing",
    "finished" (with a success/failed result), "canceled", and "timeout".

    Args:
        build_id: The build id returned by codemagic_start_build or listed by
            codemagic_list_builds.
    """
    return _ok(codemagic.get_build(build_id))


@mcp.tool()
@_safe
def codemagic_list_builds(
    app_id: str | None = None,
    workflow_id: str | None = None,
    branch: str | None = None,
    status: str | None = None,
) -> str:
    """List builds, optionally filtered by app, workflow, branch, or status.

    Args:
        app_id: Only builds for this application id.
        workflow_id: Only builds for this workflow id.
        branch: Only builds for this branch.
        status: Only builds with this status (e.g. "building", "finished").
    """
    return _ok(
        codemagic.list_builds(
            app_id=app_id,
            workflow_id=workflow_id,
            branch=branch,
            status=status,
        )
    )


@mcp.tool()
@_safe
def codemagic_cancel_build(build_id: str) -> str:
    """Cancel a running or queued build.

    Args:
        build_id: The id of the build to cancel.
    """
    return _ok(codemagic.cancel_build(build_id))


@mcp.tool()
@_safe
def codemagic_get_build_log(build_id: str, step: str | None = None, tail: int = 200) -> str:
    """Read the log of one build step, to see why a build failed.

    Without a step name it picks the first failed step, so the usual call is
    just the build id. Returns the step's name and status and the last lines
    of its log.

    Args:
        build_id: The build id (from codemagic_start_build or codemagic_list_builds).
        step: Part of a step name, e.g. "build ipa" or "code signing".
        tail: How many lines from the end of the log to return (default 200).
    """
    return _ok(codemagic.get_build_log(build_id, step=step, tail=tail))
