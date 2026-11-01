# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `codemagic_get_build_log`: reads the log of one build step (the first failed
  step unless a step name is given) and returns its last lines, so a failed
  build can be explained without opening the Codemagic UI. The API token is
  only sent to the configured Codemagic host.

## [0.1.0] - 2026-06-10

### Added

- Initial release.
- MCP tools: `codemagic_list_apps`, `codemagic_get_app`, `codemagic_start_build`,
  `codemagic_get_build`, `codemagic_list_builds`, `codemagic_cancel_build`.
- httpx-based Codemagic REST API client with `x-auth-token` auth.
- Unit tests with mocked HTTP, GitHub Actions CI (lint + test on Python 3.10–3.13).

[Unreleased]: https://github.com/musictechlab/mcp-codemagic/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/musictechlab/mcp-codemagic/releases/tag/v0.1.0
