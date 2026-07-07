# loop.md — manutenção autônoma do learnhouse (rodar com /loop sem argumentos)

Você está no loop de manutenção (Loop Engineering — CLAUDE.md §16). Uma passada = os checks abaixo,
na ordem, consertando o que for barato e reportando o que não for. Estado durável: se `.claude/runs/ACTIVE`
existir, a marathon tem prioridade — execute a "Próxima ação" do RUN.md e encerre a passada.

## Checks da passada

1. **Lessons pendentes de promoção** — `tasks/lessons.md`: alguma lição repetida 2×+ ainda sem
   `[PROMOVIDA → destino]`? Se sim, promover (regra no CLAUDE.md §apropriada ou hook via hookify) e marcar.
2. **Wiki/documentação do repo íntegra** — `python3 scripts/docs-wiki-lint.py`. FAIL → corrigir
   `docs/index.md`, `docs/log.md` ou índice da categoria (regidos por `docs/SCHEMA.md`) e re-rodar.
3. **Frescor do mining** — `bash apps/web/scripts/ds-classname-workflow-check.sh`. Stale → regenerar MD
   (`node apps/web/scripts/classname-miner-v2.mjs`), stage, e re-ingerir o Postgres
   (`bash .claude/skills/classname-token-workflow/scripts/classname-mining-ingest.sh`).
4. **Árvore git suja de artefato órfão** — `git status --short`: arquivo gerado que não deveria ser
   commitado (PDF, JSON >1MB, print solto em docs/)? Reportar com path; não deletar nada tracked sem ordem.
5. **Gates de design-system** — `bash apps/web/scripts/ds-gate.sh` (ratchet anti-hardcode). Regressão → reportar
   cluster e path:linha.
6. **Integridade referencial (backstop de rename/delete)** — `python3 scripts/ref-integrity.py --since <ref-da-última-passada-verde>`
   (report-only; o pre-commit já pega no commit, este pega bypass `--no-verify` e edição manual). Achado
   `[link]`/`[stale]` → corrigir per skill `ref-integrity` (repoint / desativar / allowlist).

## Regras do loop

- Ação irreversível (push, delete tracked, deploy, prod) = FORA do loop; apenas reportar.
- Cada passada termina com resumo de 3-6 linhas: o que passou, o que consertou, o que precisa do Augusto.
- Nada a fazer em 2 passadas seguidas → encerrar o loop (self-paced: não agendar próxima).
