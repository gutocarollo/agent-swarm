#!/usr/bin/env bash
# SessionStart hook — injeta tasks/lessons.md no contexto (CLAUDE.md §16, self-improvement loop).
# Saída em stdout vira contexto da sessão. Cap de linhas para não inflar o prompt.
set -euo pipefail
ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
FILE="$ROOT/tasks/lessons.md"
[ -f "$FILE" ] || exit 0
MAX_LINES=80
echo "<lessons-learned source=\"tasks/lessons.md\">"
echo "Lições de sessões anteriores (CLAUDE.md §16). Reler as do domínio da tarefa atual; após correção do usuário, fazer append imediato; 2ª recorrência → promover a regra/hook."
tail -n "$MAX_LINES" "$FILE"
echo "</lessons-learned>"
