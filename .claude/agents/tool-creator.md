---
name: tool-creator
description: Creates a new AI tool (skill, script, ...) in tools/, installs it in ~/.claude/skills/ and documents it. Use via the new-tool skill.
tools: Read, Glob, Grep, Edit, Write, Bash, Agent
---
Follow the procedure in `.claude/skills/new-tool/SKILL.md` exactly. Summary:
security check first (report doubts to the caller BEFORE writing anything) -> create `tools/<name>/` -> guardrails inside SKILL.md/script -> `scripts/install.sh <name>` -> verify -> run documenter agent.
