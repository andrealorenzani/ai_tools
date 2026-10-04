---
name: sftp-upload
description: Upload a file to a remote server via SFTP (default host andrealorenzani.name, dir `<host>/ai`). Use when asked to upload/publish/copy a file somewhere online or to a subdomain.
---
# sftp-upload
Run: `python3 ~/.claude/skills/sftp-upload/scripts/upload.py FILE [--host SUB.andrealorenzani.name] [--dir DIR] [--force] [--trust-new-host]`

- Defaults: host `andrealorenzani.name`, dir `<host>/ai`, e.g. `andrealorenzani.name/ai/` (created if missing, relative to login dir; for a subdomain `--host` the dir is `<subdomain host>/ai`). Other known domain: `supermaestro.org`.
- Subdomain: pass `--host`. Credentials lookup: section for the exact host, else parent domain.
- Prints `uploaded <file> -> host:path`; report that to the user.

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
- Host key checked against `~/.ssh/known_hosts`; unknown host is rejected. Use `--trust-new-host` only after the user confirms the host.
- Remote dir with `..` is rejected. Only uploads a single local file.
- First run creates venv `~/.local/share/ai-tools/venv` with `paramiko` (user-approved).
- Does not read FileZilla files.
