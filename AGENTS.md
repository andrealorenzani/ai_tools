# AI Tools repo

Personal tools for AI use (skills, scripts, ...). Source of truth lives here; copies are installed in `~/.claude/skills/`.

## Layout
- `tools/<name>/` one dir per tool; `SKILL.md` + optional `scripts/`. Installed as-is to `~/.claude/skills/<name>/`.
- `.claude/skills/`, `.claude/agents/` maintenance skills/agents for THIS repo only.
- `docs/business.md` business logic of each tool. `README.md` index of tools.
- `scripts/install.sh <name>` copies a tool to `~/.claude/skills/`.

## Triggers
- Creating/adding/changing a tool -> skill `new-tool` (agent `tool-creator`).
- Any change to tools or docs -> skill `document` (agent `documenter`) before finishing.

## Guardrails
- NEVER create `AGENTS.md`/`CLAUDE.md` in `~/.claude/`. Guardrails go inside each SKILL.md.
- NEVER write secrets in the repo or in chat. Secrets live in `~/.password` (INI, chmod 600); see `docs/business.md`.
- Security doubt -> tell the user BEFORE creating the tool.
- Never edit `~/.claude/skills/<name>` directly; edit `tools/<name>` then run `scripts/install.sh`.
- Keep docs short. Commit only when asked.
