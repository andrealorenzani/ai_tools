#!/usr/bin/env bash
# Install tool(s) from tools/<name> into ~/.claude/skills/<name>. Usage: install.sh <name>... | --all
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
dest="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$dest"
names=("$@")
[ "${1:-}" = "--all" ] && names=($(ls "$root/tools"))
[ ${#names[@]} -gt 0 ] || { echo "usage: install.sh <name>... | --all" >&2; exit 1; }
for n in "${names[@]}"; do
  [ -f "$root/tools/$n/SKILL.md" ] || { echo "missing tools/$n/SKILL.md" >&2; exit 1; }
  rm -rf "$dest/$n"; cp -r "$root/tools/$n" "$dest/$n"
  echo "installed $n -> $dest/$n"
done
