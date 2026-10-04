# AI Tools

Tools (skills, scripts) for use with AI. Source in `tools/<name>/`, installed to `~/.claude/skills/<name>/` via `scripts/install.sh`.

## Maintenance (this repo only)
| Item | Purpose |
|---|---|
| skill `new-tool` / agent `tool-creator` | Create, install and document a tool |
| skill `document` / agent `documenter` (haiku) | Keep README and docs in sync |

## Tools
| Tool | Kind | Purpose |
|---|---|---|
| sftp-upload | skill | Upload a file to a remote server via SFTP |

Business logic: [docs/business.md](docs/business.md). Secrets: `~/.password` (INI, chmod 600), never committed.
