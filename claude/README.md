# claude/ — padronização e curadoria de documentação (Claude Code)

Pacote extraído do repositório learnhouse (fork privado) em 2026-07-07, com os paths originais
anotados abaixo. Cópias sanitizadas de referências de cliente (este repositório é público).
Os índices reais (`docs/index.md`, `docs/log.md`) ficaram FORA por conterem conteúdo do projeto
privado — o padrão deles (indexação temporal dupla: índice por categoria + log cronológico
append-only `## [YYYY-MM-DD] tipo · categoria`) está especificado em `docs/SCHEMA.md` §4.

## Mapa de artefatos

| Arquivo | Path original | Papel |
|---|---|---|
| `docs/SCHEMA.md` | `docs/SCHEMA.md` | Constituição da wiki Karpathy repo-wide: naming por classe temporal (`living` = slug sem data, `event` = `YYYY-MM-DD-slug`, `sequenced` = `NNNN-slug`), frontmatter de `status`, indexação temporal, ciclo ingest/query/lint/prune e política "git é o arquivo" |
| `scripts/docs-wiki-lint.py` | `scripts/` | Lint determinístico da wiki: doc órfão sem menção em índice/log = FAIL; naming fora do §2 = WARN (migração incremental, `--strict-naming` bloqueia); cobre não-markdown |
| `scripts/ref-integrity.py` | `scripts/` | Integridade referencial git-aware de renames/deletes: links markdown mortos + citações vivas a nomes antigos. FONTE ÚNICA com 3 consumidores (`--staged` / `--range` / `--since`) |
| `scripts/design-system-wiki-lint.py` | `scripts/` | Shim de compatibilidade do lint antigo (exemplo de migração de escopo sem quebrar chamadores) |
| `githooks/pre-commit` | `.githooks/pre-commit` | Consumidor 1 do ref-integrity: bloqueia commit com referência quebrada (`--staged`, resolve contra o INDEX). Ativar com `git config core.hooksPath .githooks` |
| `skills/ref-integrity/SKILL.md` | `.claude/skills/` | Consumidor 2: skill invocável (`--range A..B`) com protocolo de correção (repoint / desativar / allowlist; nunca sed cego) |
| `loop.md` | `.claude/loop.md` | Consumidor 3 + loop de manutenção contínua estilo Boris: lint da wiki, ref-integrity `--since` (backstop de `--no-verify`), lessons a promover, árvore git suja |
| `ref-integrity-allowlist` | `.ref-integrity-allowlist` | Exceções determinísticas: auto-output de geradores e backups cuja "ausência" é esperada |
| `skills/repo-wiki-curator/SKILL.md` | `.claude/skills/` | Skill orquestradora da curadoria de `docs/` (ingest/query/lint/prune do SCHEMA) |
| `skills/learnhouse-delivery-council/SKILL.md` | `.claude/skills/` (espelho `.agents/skills/`) | Council de entrega com Planning/Execution Adversarial Loops — toda rodada de review roda OBRIGATORIAMENTE em subagent reviewer (nunca inline), rodada N+1 continua o mesmo subagent, relatório atribui executor (`REVISORES:`) |
| `skills/adversarial-review/SKILL.md` | `.claude/skills/` | Contrato da review adversarial (classes de prova por hipótese); self-review inline proibido — vira o prompt do subagent |
| `hooks/lessons-inject.sh` | `.claude/hooks/` | SessionStart hook: injeta `tasks/lessons.md` em toda sessão nova (self-improvement §16) |
| `tasks/lessons.md` | `tasks/` | Exemplo real do ciclo capturar → injetar → promover (lições `[PROMOVIDA → destino]`) |
| `github-workflows/docs-integrity.yaml` | `.github/workflows/docs-integrity.yaml` | Consumidor 4 (CI): backstop de `--no-verify`/clone sem hook — roda wiki-lint + `ref-integrity --selftest` + range do push |
| `CLAUDE.md` | `.claude/CLAUDE.md` | Curado para publicação: bloco wiki Karpathy, bloco council, LEI ZERO (não reinventar), §14 consistência DRY, §15 workflow orchestration (Boris Cherny), §16 self-improvement loop |
