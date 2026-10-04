# Business logic

## Conventions
- Credentials: `~/.password`, INI format, `chmod 600`, one `[section]` per domain/service with `key = value` lines.
- Every tool has embedded guardrails (SKILL.md section + script checks).

## sftp-upload

**Purpose**: Upload a file to a remote server via SFTP.

**Inputs**: Local file path; optional host (subdomain of andrealorenzani.name or full domain), remote directory, and flags (--force to overwrite, --trust-new-host for unknown keys).

**Behaviour**: Defaults to `andrealorenzani.name`, directory `ai`. Known domains: `andrealorenzani.name`, `supermaestro.org`. Subdomains need the full hostname in `--host`; credentials resolve from the exact host section, else the parent domain. Refuses to overwrite unless --force is used. Validates host key against `~/.ssh/known_hosts`; rejects unknown hosts unless --trust-new-host is confirmed. Rejects remote paths with `..`. Single file upload only.

**Credentials**: `~/.password` (INI, chmod 600), with one `[host]` section per domain containing `user`, `password`, and optional `port` (default 22).

**Security notes**: Script refuses to read ~/.password unless permissions are 600. First run creates venv at ~/.local/share/ai-tools/venv with paramiko. Host key validation prevents MITM. Remote directory created if missing.
