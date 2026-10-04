---
name: new-tool
description: Create a new AI tool (skill, script, ...) in this repo, install it in ~/.claude/skills and document it. Use when asked to create/add a tool or skill.
---
# new-tool
Run in the `tool-creator` agent or inline.

## Steps
1. **Security check FIRST.** If anything may be a risk (reading credential stores, executing remote code, destructive ops, network exposure, broad file access), STOP and explain to the user; wait for the answer. Ask about any other doubt too.
2. Create `tools/<name>/` (kebab-case):
   - `SKILL.md` with frontmatter `name` and a short, efficient `description` (what + when to trigger).
   - Scripts in `tools/<name>/scripts/` if the tool is not a skill itself; the SKILL.md must explain how to call them.
   - **Guardrails embedded in the tool**: a "Guardrails" section in SKILL.md and checks in the script (validate inputs, no secrets in output, confirm destructive actions).
3. Secrets: never hardcode. Read from `~/.password` (INI, chmod 600, one `[section]` per domain/service, `key = value`; e.g. `[example.org]` / `user=...` / `password=...`). Script must refuse if perms are looser than 600. Document the needed section in SKILL.md.
4. Install: `scripts/install.sh <name>` (copies to `~/.claude/skills/<name>`). Never create AGENTS.md/CLAUDE.md in `~/.claude`.
5. Test the installed copy.
6. Document: invoke skill `document`.
7. Report to the user: what was created, where, how to trigger it.
