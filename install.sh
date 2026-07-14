#!/usr/bin/env bash
# Install the /architect router and the executor sub-agent into ~/.claude/,
# so they work in EVERY project on this machine — not just this one.
#
# Routing logic is universal: the judgment-versus-typing question doesn't change
# from repo to repo. So the router belongs at user scope (Chapter 10).
#
# Non-destructive: an existing file is backed up before it is replaced.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${CLAUDE_HOME:-$HOME/.claude}"
STAMP="$(date +%Y%m%d-%H%M%S)"

install_file() {
  local from="$1" to="$2"
  mkdir -p "$(dirname "$to")"
  if [ -e "$to" ] && ! cmp -s "$from" "$to"; then
    mv "$to" "$to.backup-$STAMP"
    echo "  backed up existing -> $(basename "$to").backup-$STAMP"
  fi
  cp "$from" "$to"
  echo "  installed $to"
}

echo "installing the split-stack router into $DEST"
install_file "$SRC/skill/architect/SKILL.md" "$DEST/skills/architect/SKILL.md"
install_file "$SRC/skill/agents/executor.md" "$DEST/agents/executor.md"

cat <<EOF

Done. Two things are now available in every project you open:

  /architect <task>   classify the task, assign the seat, emit a handoff
  executor            a sub-agent pinned to Sonnet, for typing only

Try it on the demo app, which has a real bug in it:

  cd $SRC/demo/invoicing-api
  npm install && npm test
  # then, in Claude Code, from that directory:
  /architect the reconciliation job double-charges intermittently; find the cause and fix it

Then run it on a repo of your own. That transfer is the point.

/architect is an instruction file Claude Code reads and follows. It needs Claude
Code and a model to do anything. Everything else in this repo runs offline.
EOF
