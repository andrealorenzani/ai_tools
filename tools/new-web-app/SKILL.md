---
name: new-web-app
description: Bootstrap a new web application (PHP server, optional MySQL) with architecture docs, README, code-navigation guide and an agentic feature-development workflow with a documenter agent. MUST be used whenever the user starts developing a new web application / website / web project from scratch.
---
# new-web-app

Use this at the start of ANY new web application. Work in the project root (the current directory, or the one the user names). Do the steps in order.

## 1. Gather requirements and confirm stack

Ask the user (briefly, in one `AskUserQuestion` call when possible) only what you cannot infer from their request:

- **What the app does** (purpose, main users, main features) — skip if already clear.
- **Server language: PHP is the default.** If the request doesn't mention a language, state "I'll use PHP" and ask for confirmation only if something in the request hints at a different stack or the choice is genuinely ambiguous. Also settle: plain PHP vs. a framework (Slim, Laravel, Symfony…) and the PHP version, defaulting to modern PHP (>= 8.2) with Composer and PSR-4 autoloading, unless the user says otherwise.
- **Database: needed?** If the app needs persistent data, **MySQL is the default** (use PDO with prepared statements, migrations as versioned `.sql` files or the framework's migration tool). Ask for confirmation of MySQL; if the user prefers another DB, follow them. If no persistence is needed, don't add a DB. When a DB is used:
  - **Server:** default `mysql.supermaestro.org`; the connection definition (user, password, port, possibly database) is read from `~/.password` (see "MySQL access" below). Confirm host/database name with the user only if `~/.password` doesn't define them.
  - **Table prefix (MANDATORY):** every table MUST have a project prefix (e.g. `shop_`). If the user hasn't given one, ask for it (suggest one derived from the project name, e.g. `<short_name>_`). Do not proceed with any DB work without a prefix.
- **SFTP deployment (always ask, never skip):** ask whether an agent / skill is needed to upload the project files to an SFTP server. If yes, ask for the **server (host)** and the **remote root directory**. Never ask for or store passwords/keys in the repo; credentials stay in the user's SSH config / agent or env vars.
- Frontend approach only if relevant (server-rendered templates by default; JS framework only if requested).

Record the confirmed decisions; they go in the architecture doc.

## MySQL access (when a DB is used)

- Use the `mysql` command-line client to create the database/tables and run migrations against the server (default host `mysql.supermaestro.org`).
- Read the connection definition from `~/.password`. Look only for the MySQL entry; its format may vary, so if it is unclear which entry/fields apply, ask the user rather than guessing.
- Secrets handling: never print, log, echo or summarize the password; never copy credentials into the repo, docs, README, `.env.example`, agent/skill files or commit messages. Pass them to `mysql` via a temporary option file (`--defaults-extra-file`, mode 600, deleted afterwards) or environment variable. The application itself gets credentials from a git-ignored `.env`; `.env.example` holds placeholders only (`DB_HOST=`, `DB_PREFIX=` with the real prefix, which is not secret). Tracked files and docs never contain the actual host name; refer to it as "the DB entry in `~/.password`".
- Before creating or changing anything on the server, tell the user which host and database will be touched; it is a shared server. Only touch tables that carry the project prefix.

## 2. Define the architecture → `docs/architecture.md`

Write `docs/architecture.md` containing:

- Purpose and scope, main features
- Confirmed stack (PHP version, framework/none, MySQL or none, frontend, web server, dependency management)
- High-level design: layers/components (routing, controllers, services, repositories/models, views, config), request lifecycle, and a diagram (Mermaid)
- Directory layout with the role of each directory
- Data model (tables, key relations) if a DB is used; the mandatory **table prefix**; the name of the `~/.password` entry that holds the DB connection (e.g. `[mysql]`), never the host name, user, password or port; how migrations are run
- Cross-cutting concerns: configuration/secrets (env vars, never committed), error handling, logging, authentication/authorization, validation, security (CSRF, XSS escaping, SQL injection via prepared statements, password hashing)
- Testing strategy (e.g. PHPUnit) and how to run tests
- Key decisions with short rationale (ADR-style list), and open questions

Then create the initial project skeleton consistent with it (composer.json, `public/index.php` front controller, `src/`, `config/`, `templates/`, `tests/`, `.gitignore`, `.env.example`, and `migrations/` if MySQL). Keep the skeleton minimal and runnable (`php -S localhost:8000 -t public`). Verify it runs.

## 3. Write `README.md` and `docs/changelog.md`

Also create `docs/changelog.md` with a short header (format: Keep a Changelog, semantic versioning), an empty `## [Unreleased]` section and an initial `## [0.1.0] - <today>` entry "Initial project skeleton". It is maintained by the `documenter` agent; set the same version in `composer.json` and mention the current version in the README.


Project description, requirements, install/setup (composer install, copy `.env.example`, create DB and run migrations if any), how to run and test, project structure summary, and a pointer to `docs/` and to the agentic workflow (section 4).

## 4. Code the agentic workflow for new features

Create project-level Claude Code files so future features follow a repeatable, doc-driven process.

### `.claude/agents/documenter.md`
```markdown
---
name: documenter
description: Keeps the project documentation (docs/architecture.md, docs/code.md, docs/changelog.md, README.md) in sync with the code. Use after any feature is implemented or code structure changes.
tools: Read, Grep, Glob, Edit, Write, Bash
---
You are the documenter. Given a description of what changed (or by inspecting `git diff` / `git status`),
update the documentation so it matches the code:
- `docs/architecture.md`: only for architectural changes (new components, data model/migrations, new decisions → add to the decisions list).
- `docs/code.md`: add/rename/remove entries for files, classes, routes, tables, and entry points that changed.
- `README.md`: setup/run/feature-list changes.
- `docs/changelog.md`: the changelist, one section per version (Keep a Changelog style: `## [x.y.z] - YYYY-MM-DD` with Added / Changed / Fixed / Removed / Security / Database subsections). Record every user-visible or structural change under `## [Unreleased]`; when a version is released (user asks, or a version bump is requested), rename it to the new version with the date and open a fresh `[Unreleased]`. Follow semantic versioning (breaking → major, feature → minor, fix → patch) and propose the bump; list migrations and schema changes (with prefixed table names) under Database. Never rewrite past versions.
Rules: verify every claim against the code (never document what you haven't seen); keep the existing style
and brevity; do not touch source code; remove stale entries; report a short summary of the doc changes.
```

### `.claude/agents/` other agents (create these too)
- `architect.md` — reads `docs/architecture.md` and `docs/code.md`, produces a short implementation plan for a feature (files to touch, data/migration changes, risks) respecting existing decisions; read-only tools (Read, Grep, Glob). Flags when the feature requires an architecture change.
- `implementer.md` — implements a given plan following the conventions in `docs/`; writes tests with the code; runs the test suite; tools: all file/Bash tools.
- `reviewer.md` — read-only review of the diff for correctness, security (OWASP basics, SQL injection/XSS/CSRF), consistency with `docs/architecture.md`, and test coverage; returns a prioritized list of issues.

Give each a precise `description` and a focused system prompt.

### `.claude/commands/feature.md` (slash command `/feature <description>`)
The orchestrating workflow. Content (adapt wording, keep the sequence):
1. Read `docs/architecture.md` and `docs/code.md` to understand constraints and where code lives.
2. If the request is ambiguous, ask the user to clarify before proceeding.
3. Spawn `architect` with the feature description → plan. If the plan changes the architecture, show it to the user and get confirmation.
4. Spawn `implementer` with the plan → code + tests; tests must pass.
5. Spawn `reviewer` on the result; send blocking issues back to `implementer` (max 2 loops), then report remaining issues to the user.
6. Spawn `documenter` with a summary of what changed → docs updated, including an entry in `docs/changelog.md` under `[Unreleased]`.
7. Report to the user: what was built, files changed, test results, doc updates.

### `CLAUDE.md` (project root)
Also create `AGENTS.md` with the same content (or a one-line pointer to `CLAUDE.md`) so other agent tools pick it up. Short: stack summary, how to run/test, "read `docs/architecture.md` and `docs/code.md` before making decisions or searching the code", "new features go through `/feature`", "after any code change that alters structure, invoke the `documenter` agent".
If a DB is used, it MUST also contain a prominent **Database rules** section, verbatim in spirit:
- "ALL tables MUST be named with the prefix `<prefix>`. Never create, alter, query or drop a table without it; never touch tables without it."
- DB connection: the name of the `~/.password` entry and the table prefix may be written in the repo; the host name, user, password and port come from `.env` / `~/.password` and are never written in the repo, docs, zip or printed.
- "Every agent and skill in this project must follow these rules."

Enforcement: the `architect`, `implementer`, `reviewer` and `documenter` agents (and `/feature`, `/deploy`) must each state in their prompt "follow the Database rules in CLAUDE.md: all tables use the prefix `<prefix>`"; the `reviewer` treats any unprefixed table (in migrations, queries, ORM mappings, tests) as a blocking issue; the `implementer` builds table names from the configured `DB_PREFIX` rather than hard-coding where practical; the `documenter` records the prefix in `docs/architecture.md` and `docs/code.md`.

## 5. Write `docs/code.md` — code navigation guide

A map to find things fast, derived from the real code (not guessed):
- Entry points (front controller, CLI scripts) and request flow with file references
- Directory-by-directory description
- Routing table: method + path → controller/handler (file:line style references where practical)
- Key classes/modules: one line each on responsibility
- Database: tables → model/repository files, migration location
- Config and environment variables
- Templates/views and where they're rendered
- Tests: where they are, how to run, naming conventions
- "Where do I…" cheat sheet (add a route, add a page, add a migration, add a test)

Mark at the top that the `documenter` agent maintains this file.

## 6. SFTP upload agent / skill (only if the user said yes in step 1)

Using the confirmed host and remote root directory:

- Create `.claude/agents/deployer.md`: uploads the project's deployable files (e.g. `public/`, `src/`, `config/`, `templates/`, `vendor/` after `composer install --no-dev`, `migrations/`) to `<host>:<root>`; excludes `.git`, `.claude`, `docs`, `tests`, `.env`, and local-only files; shows the list of files to upload and asks the user for confirmation before uploading (publishing is outward-facing); reports what was uploaded. Tools: Read, Glob, Bash.
- Create `.claude/skills/deploy/SKILL.md` (project skill, `/deploy`) holding the upload procedure, with host and root directory written as the single source of truth (also noted in `docs/architecture.md` and `README.md`). Prefer reusing the machine-wide `sftp-upload` skill (`python3 ~/.claude/skills/sftp-upload/scripts/upload.py FILE --host HOST --dir DIR`) when it fits; otherwise use `sftp`/`rsync` over SSH with a batch file.
- Mention `/deploy` in `CLAUDE.md` and in the `/feature` workflow as an optional last step, only when the user asks to deploy.
- If the user said no, record "no SFTP deployment" in `docs/architecture.md` and create nothing.

## 6b. Release command and rules (always)

Copy `~/.claude/skills/new-web-app/release/SKILL.md` (the machine-wide `release` skill) into the project as `.claude/commands/release.md` (replace the frontmatter with `description: Cut a major release` and `argument-hint: [version]`; keep the body; replace `<project>` and the test command). Then:
- `CLAUDE.md` gets a **Release** rule: "Releases are major (`N.0.0`, first is `1.0.0`) and go through `/release`: version bump, refactor, docs refresh, ADRs consolidated into `docs/decisions/0001-before_release.md` (template kept), `release/<version>/` with `<version>.zip` (code + `docs/`) and a changelog copy, tests, commit, deploy. `release/` is never deployed nor web-served; never put host/credentials in the zip."
- `.claude/agents/documenter.md` gets: "On `/release`: cut the changelog heading and `VERSION`, refresh all docs, write `docs/decisions/0001-before_release.md` summarising all ADRs (decided, why, trade-offs, constraints in force, rejected alternatives; no algorithms, no confidentiality leaks), fix references to removed ADRs."
- The deploy script/deployer agent must exclude `release/`, and the web root must not serve it.
- Mention `/release` in the README/DEVELOPER docs workflow section.

## 7. Finish

Run the app and tests once to verify the skeleton works. Summarize to the user: decisions taken (PHP / MySQL / SFTP confirmations), files created, and how to start building features with `/feature <description>`. Do not commit unless asked.
