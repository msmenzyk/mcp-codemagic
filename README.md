# mcp-codemagic

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/musictechlab/mcp-codemagic/actions/workflows/ci.yml/badge.svg)](https://github.com/musictechlab/mcp-codemagic/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![MCP](https://img.shields.io/badge/MCP-1.0+-purple.svg)](https://modelcontextprotocol.io/)
[![Built by MusicTech Lab](https://musictechlab.io/oss/build-by-musictechlab.io.svg)](https://musictechlab.io)

An [MCP](https://modelcontextprotocol.io) server for [Codemagic](https://codemagic.io) CI/CD. Trigger and inspect mobile/Flutter builds straight from Claude Code (or any MCP client) using the [Codemagic REST API](https://docs.codemagic.io/rest-api/overview/).

> Built and maintained by [MusicTech Lab](https://musictechlab.io).

## Features

| Tool | Description |
|------|-------------|
| `codemagic_list_apps` | List all applications and their workflow ids |
| `codemagic_get_app` | Get one application's repo, branches, and workflows |
| `codemagic_start_build` | Trigger a build for an app/workflow on a branch or tag |
| `codemagic_get_build` | Get the status and details of a build |
| `codemagic_list_builds` | List builds, filterable by app/workflow/branch/status |
| `codemagic_cancel_build` | Cancel a running or queued build |

## Requirements

- Python 3.10+
- [Poetry](https://python-poetry.org/)
- A Codemagic API token

## Setup

```bash
git clone https://github.com/musictechlab/mcp-codemagic.git
cd mcp-codemagic
poetry install
cp .env.example .env   # then fill in CODEMAGIC_API_KEY
```

### Getting your API token

In Codemagic, go to **User settings → Integrations → Codemagic API** (or **Team settings → Integrations** for team accounts) and copy the token. Put it in `.env`:

```dotenv
CODEMAGIC_API_KEY=your-codemagic-api-token
```

## Running

```bash
poetry run python -m mcp_codemagic
# or, via the installed console script:
poetry run mcp-codemagic
```

## Connecting to Claude Code

Add the server with the CLI:

```bash
claude mcp add codemagic -- poetry --directory /absolute/path/to/mcp-codemagic run python -m mcp_codemagic
```

Or add it manually to your MCP config:

```json
{
  "mcpServers": {
    "codemagic": {
      "command": "poetry",
      "args": ["--directory", "/absolute/path/to/mcp-codemagic", "run", "python", "-m", "mcp_codemagic"],
      "env": { "CODEMAGIC_API_KEY": "your-codemagic-api-token" }
    }
  }
}
```

## Example prompts

- "List my Codemagic apps and their workflows."
- "Start the `ios-release` workflow for app `<app-id>` on `main`."
- "What's the status of build `<build-id>`?"
- "Show the last builds for app `<app-id>` that are still building."
- "Cancel build `<build-id>`."

## Examples

### List apps

> "List my Codemagic apps and their workflows."

Calls `codemagic_list_apps` and returns each application with its id and workflow ids:

```json
{
  "applications": [
    {
      "_id": "6a28af80c12e620808693f7b",
      "appName": "vimoswim-coach",
      "repository": { "htmlUrl": "https://github.com/vimoswim/vimoswim-coach" },
      "workflowIds": ["6a28af80c12e620808693f7a"]
    }
  ]
}
```

### Trigger a build

> "Start workflow `6a28af80c12e620808693f7a` for app `6a28af80c12e620808693f7b` on `main`."

Calls `codemagic_start_build` and returns the new build id:

```json
{ "buildId": "6a28f92cf7acee31a7394057" }
```

### Check build status

> "What's the status of build `6a28f92cf7acee31a7394057`?"

Calls `codemagic_get_build`. The `status` field moves through `queued → building → finishing → publishing → finished`:

```json
{
  "build": {
    "_id": "6a28f92cf7acee31a7394057",
    "status": "queued",
    "branch": "main",
    "workflowId": "6a28af80c12e620808693f7a",
    "instanceType": "mac_mini_m2"
  }
}
```

Errors come back as JSON (never raised), so the agent can read them:

```json
{ "error": "Codemagic API 404 for GET /builds/missing", "status": 404, "body": { "message": "Build not found" } }
```

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CODEMAGIC_API_KEY` | yes | — | Codemagic API token (`x-auth-token`) |
| `CODEMAGIC_BASE_URL` | no | `https://api.codemagic.io` | Override the API base URL |

## Development

```bash
poetry install
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

To report a vulnerability, see [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
  MusicTech Lab - Rockstars Developers dedicated to the Music Industry<br>
  <a href="https://musictechlab.io">Website</a>
  <span> | </span>
  <a href="https://linkedin.com/company/musictechlab">LinkedIn</a>
  <span> | </span>
  <a href="https://musictechlab.io/contact">Let's talk</a><br>
  Crafted by <a href="https://musictechlab.io">musictechlab.io</a>
</div>
