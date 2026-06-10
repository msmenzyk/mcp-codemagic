# Security Policy

## Reporting a vulnerability

If you discover a security vulnerability in `mcp-codemagic`, please report it
privately. **Do not open a public issue.**

Email **opensource@musictechlab.io** with:

- A description of the vulnerability and its impact
- Steps to reproduce
- Any suggested remediation

We aim to acknowledge reports within 3 business days and to provide a remediation
timeline after triage.

## Scope & handling secrets

- Your Codemagic API token grants control over your CI/CD builds. Treat it like a
  password.
- The token is read from the `CODEMAGIC_API_KEY` environment variable or a local
  `.env` file, which is gitignored. Never commit it.
- This server makes authenticated calls to `https://api.codemagic.io` on your
  behalf and returns the API responses to the MCP client. Review which tools you
  expose in shared or automated environments.

## Supported versions

The latest released version on `main` receives security fixes.
