---
name: release
description: Cut and ship a (major) release of a project built with the new-web-app workflow. Use when the user asks to release, cut a release, ship version N.0.0, "make release 1.0.0", or publish a new major version. Refactors, updates docs, consolidates ADRs, builds a release zip, commits and deploys.
---
# release

Orchestrated by the main agent. The orchestrator writes no code or docs itself: code and tests go to `implementer`/`reviewer`, docs (incl. `VERSION`, changelog, ADRs under `docs/`) go to `documenter`, upload goes to `deployer`/the project deploy script. Read `CLAUDE.md`, `docs/architecture.md`, `docs/code.md` first. Use the project's test command below (`php tests/run.php` in PHP projects without PHPUnit; otherwise the command in CLAUDE.md). Do the steps in order.

## Safety rules (apply to every step)
- Never write the server host, domain, hosting provider or credentials into any tracked file, the zip, the commit message or agent output. Deployment and DB settings stay in gitignored files (`.deploy.local`, `config.php`, `.env`, `~/.password`). Allowed in tracked files: the name of the `~/.password` entry used for the DB and the table prefix (neither is secret); never the DB host name, user, password or port.
- Describe features, never algorithms, in docs and the consolidated ADR (follow the project's CLAUDE.md rules).
- Start from a clean tree (`git status` empty) on the main branch; if not, stop and ask.
- Behaviour must not change during refactor; tests stay green after every step.
- Decisions are not lost: the removed ADRs remain in git history (tag below).

## 1. Determine the version
- Releases are major: `N.0.0`, N >= 1. The first release is `1.0.0`. Read `VERSION` (if present) and `docs/changelog.md`; next = (current major + 1).0.0, or `1.0.0` if none yet (0.x -> 1.0.0).
- If the user gave a version, use it. If ambiguous (different version requested, non-major, unclear current version) ask the user to confirm before going on.
- Tag the pre-release state so the removed ADRs stay reachable: `git tag pre-release-<version>` (local; do not push unless asked).
- Have the `documenter` set `VERSION` (if the project has it, plus `composer.json`/badges if present) and cut the changelog: rename `Unreleased` to `<version> - <date>` and open a fresh empty `Unreleased`.

## 2. Refactor code and tests
- `implementer`: make code and tests clean and optimal (remove dead code, duplication, stale comments, slow or flaky tests; consistent naming), strictly without behaviour change and without touching constraints in CLAUDE.md. Run the test command.
- `reviewer`: review the diff for behaviour changes, regressions, and drift; blocking findings go back to `implementer`. Max 3 review rounds, then report leftovers to the user. Keep the reviewer's "Docs drift" list.
- Tests must be green before continuing.

## 3. Update all docs
`documenter`, given the reviewer's drift list and the refactor summary, makes these accurate and optimised: `docs/architecture.md`, `docs/code.md` (every source file listed, "Where do I..." table), `docs/features.md`, `docs/roadmap.md`, `README.md`, `DEVELOPER.md` (if present), `docs/changelog.md` (release entry summarising the version). Verify every path and command mentioned exists/works. Update badges if the project has them.

## 4. Consolidate the decisions (before the zip)
- `documenter` generates `docs/decisions/0001-before_release.md` from the template (`0000-template.md`) with Status: accepted, summarising everything useful from ALL existing ADRs: what was decided, why, trade-offs, constraints still in force, rejected alternatives, and open risks. Group by theme, not file by file; mention the old ADR numbers only as plain text (no links). No algorithms, host names or credentials.
- Then remove every other file in `docs/decisions/` except `0000-template.md` and the new `0001-before_release.md` (`git rm`). Future ADRs continue from `0002`.
- `documenter` fixes every doc reference to removed ADR files (README, architecture, code map, roadmap, changelog links -> plain text or link to `0001-before_release.md`); `implementer` fixes tests/scripts/code comments that read, link or enumerate ADR files (e.g. docs-consistency tests). Grep the whole repo for `docs/decisions/` and `decisions/00` to be sure. Run the tests: green.
- Update the architect/implementer/documenter agent prompts only if they reference specific ADR files (via `documenter`/`implementer`).

## 5. Prepare `release/`
- Create `release/` at the repo root. It must be excluded from deployment and from web access:
  - add `release/` to the deploy script's exclusion (e.g. skip paths starting with `release/` when listing files, in `scripts/deploy.sh`; update the deployer agent text) via `implementer`, with a test or dry-run check that no `release/` path would be uploaded;
  - the web root must not serve it: if `release/` is outside the public directory (e.g. `public/`) that is enough; otherwise add a deny rule (`.htaccess` `Require all denied` or the web server equivalent);
  - add `release/*.zip`-style ignore only if the user wants the artifacts out of git; by default the release folder is tracked so the history keeps the artifacts (ask if the zip is large).
- Verify with the deploy script's dry-run that nothing from `release/` is listed.

## 6. Commit the release content
Run the tests, then commit everything done so far (version bump, refactor, docs, ADR consolidation, deploy exclusion). Message mentions the release, e.g. `Release <version>: refactor, docs refresh, ADRs consolidated`. Add the project's attribution line if the environment requires it.

## 7. Build the artifacts (zip last)
Use tracked files of the release commit so the zip is consistent and gitignored files are excluded automatically:
```
V=<version>; mkdir -p release/$V
git archive --format=zip --prefix=<project>-$V/ -o release/$V/$V.zip HEAD \
  -- . ':(exclude)release' ':(exclude).deploy*' ':(exclude)config.php' ':(exclude).env' ':(exclude).env.local' ':(exclude).env.*.local' ':(exclude)cache' ':(exclude).claude/settings.local.json'
cp docs/changelog.md release/$V/changelog.md
```
(Do NOT use a broad `.env.*` exclude: it drops `.env.example`. Keep the example/template config files such as `config.php.example`, `.env.example`; adjust excludes to the project's real secret/cache names.) The zip contains all code and the `docs/` directory; it must exclude: `.git`, `release/`, secrets/config files, gitignored files, caches, `.deploy*` files. `.git` is never in `git archive`.
- Verify: `unzip -l release/$V/$V.zip` — check no secrets, no `release/`, no `.git`, no `.deploy*`, no real config, no cache; `docs/` and `docs/changelog.md` present, `docs/decisions/` has only the template and `0001-before_release.md`. Also grep the listing and the zip contents for the host/domain/provider strings and credentials patterns (the `~/.password` entry name and table prefix are allowed and must not be flagged) (look at `.deploy.local` keys only to build the search, never print them). If anything is wrong, fix and rebuild.

## 8. Final test, commit artifacts, deploy
- Run the test command again.
- Commit the `release/<version>/` artifacts (`Release <version>: add release artifacts`), unless the user chose to keep release/ untracked.
- Run the project's deploy step (`scripts/deploy.sh`, or the `deployer` agent); `release/` must not be uploaded. Report upload result without host names.
- Final summary to the user: version, what was refactored, docs updated, ADRs consolidated (old ones are in git history and tag `pre-release-<version>`), zip path and size, listing check result, tests, commit hashes, deploy result, follow-ups.
