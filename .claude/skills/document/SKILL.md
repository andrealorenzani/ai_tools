---
name: document
description: Update repo docs (README.md, docs/business.md) after tools change. Use when tools are added/edited or docs look stale.
model: haiku
---
# document
Guardrails: docs only, no secrets, no tool code changes.

Delegate to the `documenter` agent (Agent tool, subagent_type `documenter`) with a one-line note on what changed. Then check `README.md` and `docs/business.md` mention every dir in `tools/`.
