# Business logic

## Conventions
- Credentials: `~/.password`, INI format, `chmod 600`, one `[section]` per domain/service with `key = value` lines.
- Every tool has embedded guardrails (SKILL.md section + script checks).

## sftp-upload

**Purpose**: Upload a file to a remote server via SFTP.

**Inputs**: Local file path; optional host (subdomain of andrealorenzani.name or full domain), remote directory, and flags (--force to overwrite, --trust-new-host for unknown keys).

**Behaviour**: Defaults to `andrealorenzani.name`, directory `<host>/ai` (e.g. `andrealorenzani.name/ai/`; `--dir` overrides). Known domains: `andrealorenzani.name`, `supermaestro.org`. Subdomains need the full hostname in `--host`; credentials resolve from the exact host section, else the parent domain. Refuses to overwrite unless --force is used. Validates host key against `~/.ssh/known_hosts`; rejects unknown hosts unless --trust-new-host is confirmed. Rejects remote paths with `..`. Single file upload only.

**Credentials**: `~/.password` (INI, chmod 600), with one `[host]` section per domain containing `user`, `password`, and optional `port` (default 22).

**Security notes**: Script refuses to read ~/.password unless permissions are 600. First run creates venv at ~/.local/share/ai-tools/venv with paramiko. Host key validation prevents MITM. Remote directory created if missing.

## new-web-app

**Purpose**: Bootstrap a new web application (PHP server, optional MySQL) with architecture docs, README, code-navigation guide, changelog and an agentic `/feature` workflow.

**Inputs**: Project purpose and features; PHP version (default >= 8.2, Composer, PSR-4); framework or plain PHP; whether a DB is needed (MySQL default); table prefix (mandatory when a DB is used); SFTP deployment yes/no and, if yes, host and remote root directory.

**Behaviour**: Works in the project root. Asks for missing requirements, writes `docs/architecture.md`, a minimal runnable skeleton (`public/`, `src/`, `config/`, `templates/`, `tests/`, `migrations/` if MySQL), `README.md`, `docs/changelog.md` (starts at 0.1.0), project agents (`documenter`, `architect`, `implementer`, `reviewer`, optional `deployer`), `/feature` command, and `CLAUDE.md`. Copies the bundled `release` skill into the project as `.claude/commands/release.md`. Does not commit unless asked.

**Credentials**: MySQL connection (user, password, port, optional database) read from the MySQL entry of `~/.password`. Default host `mysql.supermaestro.org`. The application itself reads credentials from a git-ignored `.env`; `.env.example` holds placeholders only. Project docs/zips may name the `~/.password` entry and the table prefix, never the DB host, user, password or port (`release` checks this). SFTP credentials are never stored in the repo (SSH config, agent or env vars).

**Security notes**: Password is never printed, logged, echoed, summarised, or copied into the repo, docs, `.env.example`, agent or skill files, or commit messages; it is passed to `mysql` through a temporary option file (mode 600, deleted afterwards) or an environment variable. Before any server change the user is told which host and database will be touched (shared server). Every table carries the mandatory project prefix; unprefixed tables are a blocking review issue. Only prefixed tables are touched. The generated `CLAUDE.md` tells every agent to follow these Database rules.

## release

**Purpose**: Cut and ship a major release (`N.0.0`, first is `1.0.0`) of a project built with the new-web-app workflow: version bump, refactor without behaviour change, docs refresh, ADR consolidation, zip artifact, commit and deploy.

**Inputs**: Requested version (optional; otherwise derived from `VERSION` and `docs/changelog.md`, next major). Asks the user when the version is ambiguous or non-major.

**Behaviour**: Requires a clean tree (`git status` empty) on the main branch, otherwise stops and asks. Tags `pre-release-<version>` locally (not pushed unless asked). Refactors code and tests via `implementer`/`reviewer` (max 3 review rounds); docs via `documenter`. Consolidates all ADRs into `docs/decisions/0001-before_release.md` and removes the others with `git rm` (they remain in git history under the tag). Builds `release/<version>/<version>.zip` with `git archive` from the release commit (excludes `release/`, `.deploy*`, `config.php`, `.env*`, caches, `.claude/settings.local.json`) and a copy of the changelog. Verifies the zip listing, commits the artifacts, runs the project deploy step, where `release/` must not be uploaded.

**Credentials**: None read by the skill itself; deployment settings stay in git-ignored files (`.deploy.local`, `config.php`, `.env`, `~/.password`).

**Security notes**: Never writes server host, domain, provider or credentials into any tracked file, the zip, commit messages or agent output. Zip and listing are grepped for host/domain strings and credential patterns; the search is built from keys without printing values. `release/` is excluded from deployment and must not be web-served. Describes features, not algorithms, in docs and the consolidated ADR. Nested copy `tools/new-web-app/release/SKILL.md` must stay identical to `tools/release/SKILL.md`.
