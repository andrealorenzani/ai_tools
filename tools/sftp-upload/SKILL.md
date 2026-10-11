---
name: sftp-upload
description: Upload or delete files on a remote server via SFTP, and trust the server's SSH host key (default host andrealorenzani.name, dir `<host>/ai`). Use when asked to upload/publish/copy a file somewhere online or to a subdomain, to remove/delete/cancel a file from the server, or when the host key is unknown.
---
# sftp-upload
Run: `python3 ~/.claude/skills/sftp-upload/scripts/upload.py FILE [--host SUB.andrealorenzani.name] [--dir DIR] [--force]`

- Defaults: host `andrealorenzani.name`, dir `<host>/ai`, e.g. `andrealorenzani.name/ai/` (created if missing, relative to login dir; for a subdomain `--host` the dir is `<subdomain host>/ai`). Other known domain: `supermaestro.org`.
- Subdomain: pass `--host`. Credentials lookup: section for the exact host, else parent domain.
- Prints `uploaded <file> -> host:path`; report that to the user.

## Delete
`python3 ~/.claude/skills/sftp-upload/scripts/delete.py NAME... [--host H] [--dir D] [--list] [--rmdir] [--yes]`
- Dry run by default (prints `would delete ...`). Show that to the user, get an explicit OK, then rerun with `--yes`.
- `--list` shows the dir. NAME is a plain file name inside `--dir` (default `<host>/ai`): no slashes, wildcards or directories. `--rmdir` also removes `--dir` only if it ends up empty. Deleting a page: also remove its URL from `sitemap.xml` (merge, never replace).

## Trust host
`python3 ~/.claude/skills/sftp-upload/scripts/trust_host.py [--host H] [--yes]`
- Needed when upload/delete fail with an unknown host key. Without `--yes` it only prints the fingerprint. Show it to the user, ask them to confirm it, then rerun with `--yes` (appends to `~/.ssh/known_hosts`).
- Refuses if a different key is already known for the host (possible MITM): tell the user, do not edit known_hosts.

## Pages
Uploading a page a browser will display (`.html`, `.php`, a generated report) to a web root: apply the `seo-page` skill first. Public page -> `python3 ~/.claude/skills/seo-page/scripts/seo_check.py FILE --url <final URL>` must have no FAIL, and the site's `sitemap.xml` gets the URL (merge, never replace). Private page or report -> it must carry `<meta name="robots" content="noindex,nofollow">` (`seo_check.py FILE --private`). If it is unclear whether the page is meant to be found, ask.

## Credentials
`~/.password`, INI, `chmod 600` (script refuses otherwise). One section per host:
```
[andrealorenzani.name]
host = andrealorenzani.name   ; optional, defaults to section name
user = ...
password = ...
port = 22                     ; optional
```
Never print, log or echo this file. If a section is missing, ask the user to add it; do not ask for the password in chat.

## Guardrails
- Refuses to overwrite an existing remote file without `--force`; ask the user before using it.
- Host key checked against `~/.ssh/known_hosts`; unknown host is rejected. Use `trust_host.py` after the user confirms the fingerprint (upload's `--trust-new-host` is a legacy shortcut; avoid).
- Remote dir with `..` is rejected. Upload takes a single local file; delete never removes directories recursively and never operates on the login dir.
- First run creates venv `~/.local/share/ai-tools/venv` with `paramiko` (user-approved).
- Does not read FileZilla files.
