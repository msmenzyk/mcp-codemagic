# mcp-codemagic

MCP server for the Codemagic CI/CD REST API.

## Tech Stack

- **Language**: Python 3.10+
- **Package manager**: Poetry
- **HTTP client**: httpx
- **MCP framework**: FastMCP (mcp[cli])
- **Config**: python-dotenv (reads `CODEMAGIC_API_KEY` from `.env`)
- **Linter**: Ruff
- **Test framework**: pytest

## Commands

| Action | Command |
|--------|---------|
| Install | `poetry install` |
| Run server | `poetry run python -m mcp_codemagic` |
| Test | `poetry run pytest` |
| Lint | `poetry run ruff check .` |
| Format | `poetry run ruff format .` |

## Architecture

- `src/mcp_codemagic/server.py` — FastMCP tool definitions (one tool per Codemagic action). The `_safe` decorator turns `CodemagicError` into JSON instead of raising.
- `src/mcp_codemagic/codemagic.py` — Thin httpx client for the Codemagic REST API. Auth via the `x-auth-token` header, token from `CODEMAGIC_API_KEY`.
- `src/mcp_codemagic/__main__.py` — Entry point (`python -m mcp_codemagic` / `mcp-codemagic`).

## Codemagic API notes

- Base URL: `https://api.codemagic.io` (override with `CODEMAGIC_BASE_URL`).
- Auth header: `x-auth-token: <token>` (NOT Bearer).
- `GET /apps` → applications + their workflow ids.
- `POST /builds` with `{appId, workflowId, branch|tag}` → `{buildId}`.
- `GET /builds/{id}` → build status (`queued`, `building`, `finishing`, `publishing`, `finished`, `canceled`, `timeout`).
- `POST /builds/{id}/cancel` → cancel.

## Conventions

- Never catch broad exceptions — catch `CodemagicError` / specific `httpx.HTTPError`.
- Run `ruff check .` and `ruff format --check .` before every push.
- Secrets only via env / `.env` (gitignored). Never hardcode the token.
