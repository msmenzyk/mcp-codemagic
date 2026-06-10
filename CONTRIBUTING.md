# Contributing to mcp-codemagic

Thanks for your interest in contributing! This project is maintained by
[MusicTech Lab](https://musictechlab.io).

## Getting started

```bash
git clone https://github.com/musictechlab/mcp-codemagic.git
cd mcp-codemagic
poetry install
cp .env.example .env   # add your CODEMAGIC_API_KEY for manual testing
```

## Development workflow

1. Create a branch off `main` using a prefix: `feature/`, `fix/`, `chore/`, or `docs/`.
2. Make your change. Add or update tests under `tests/`.
3. Run the checks locally — all must pass:
   ```bash
   poetry run ruff check .
   poetry run ruff format --check .
   poetry run pytest
   ```
4. Open a pull request against `main` and fill in the PR template.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`,
`docs:`, `chore:`, `refactor:`, `test:`, `style:`. Keep the subject under 72 chars.

## Code style

- Python 3.10+, formatted and linted with Ruff (`line-length = 120`).
- Catch specific exceptions (e.g. `CodemagicError`, `httpx.HTTPError`) — never bare
  `except:` or broad `except Exception:`.
- Never commit secrets. The Codemagic token must come from the environment / `.env`.

## Reporting bugs / requesting features

Open an issue using the templates in `.github/ISSUE_TEMPLATE/`.

By contributing, you agree that your contributions are licensed under the
project's [MIT License](LICENSE).
