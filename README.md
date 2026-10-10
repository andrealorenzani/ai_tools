# AI Tools

Tools (skills, scripts) for use with AI. Source in `tools/<name>/`, installed to `~/.claude/skills/<name>/` via `scripts/install.sh`.

## Maintenance (this repo only)
| Item | Purpose |
|---|---|
| skill `new-tool` / agent `tool-creator` | Create, install and document a tool |
| skill `document` / agent `documenter` (haiku) | Keep README and docs in sync |

## Tools
| Tool | Kind | Purpose | Usage |
|---|---|---|---|
| sftp-upload | skill | Upload a file to a remote server via SFTP | `python3 ~/.claude/skills/sftp-upload/scripts/upload.py FILE --host HOST` or ask Claude to upload a file |
| new-web-app | skill | Bootstrap a PHP/MySQL web app with docs, agents, `/feature` workflow and optional SFTP deploy | Ask Claude to start a new web app; copies `release` into the project as `/release` |
| release | skill | Cut a major `N.0.0` release: refactor, docs, ADR consolidation, zip, commit, deploy | Ask Claude to release `N.0.0`, or run `/release` in a new-web-app project |

Business logic: [docs/business.md](docs/business.md). Secrets: `~/.password` (INI, chmod 600), never committed.
