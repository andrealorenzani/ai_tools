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
| sftp-upload | skill | Upload/delete files on a remote server via SFTP; trust its host key | `scripts/upload.py FILE --host HOST`, `delete.py NAME... [--yes]`, `trust_host.py [--yes]` (under `~/.claude/skills/sftp-upload/`), or ask Claude |
| new-web-app | skill | Bootstrap a PHP/MySQL web app with docs, agents, `/feature` workflow and optional SFTP deploy | Ask Claude to start a new web app; copies `release` into the project as `/release` |
| seo-page | skill | SEO checklist, page linter and sitemap merger; applied whenever a displayed page (HTML, PHP, report) is created or published | Triggers on page creation; `python3 ~/.claude/skills/seo-page/scripts/seo_check.py FILE_OR_URL [--url CANONICAL] [--private]`, `sitemap.py --out sitemap.xml --merge URL URL...` |
| release | skill | Cut a major `N.0.0` release: refactor, docs, ADR consolidation, zip, commit, deploy | Ask Claude to release `N.0.0`, or run `/release` in a new-web-app project |

Business logic: [docs/business.md](docs/business.md). Secrets: `~/.password` (INI, chmod 600), never committed.
