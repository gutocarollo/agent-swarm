---
name: ref-integrity
description: Use para detectar REFERÊNCIAS QUEBRADAS a arquivos renomeados ou deletados no repo LearnHouse — links markdown que não resolvem e citações vivas a nomes/paths antigos em md/json/txt/py/sh/toml/css. Aciona quando a tarefa mencionar: renomeei/movi/deletei arquivos e quero achar refs órfãs, verificar links quebrados, validar integridade após curadoria/rename em massa, ou revisar um range de commits. Fonte única `scripts/ref-integrity.py`; também roda como pre-commit e no loop.
---

# Ref Integrity

Integridade referencial git-aware. **Fonte única de lógica:** `scripts/ref-integrity.py` (SRP: uma
responsabilidade — nenhuma referência viva aponta para um path renomeado/deletado). Três adaptadores
finos consomem o mesmo script (DRY): pre-commit (`.githooks/pre-commit --staged`), esta skill (`--range`),
o loop (`.claude/loop.md --since`). Ver `docs/SCHEMA.md` §5 ("git é o arquivo").

## Quando usar

Depois de renomear/mover/deletar arquivos (curadoria, migração de naming, prune), ou ao revisar um PR/range,
para garantir que nenhum md/json/txt/py/sh/toml/css ainda cita o nome antigo.

## Como rodar

```bash
# um range de commits (ex.: desde antes da curadoria)
python3 scripts/ref-integrity.py --range <BASE>..HEAD
# desde um ref (uso do loop)
python3 scripts/ref-integrity.py --since <ref>
# o que está staged agora (o mesmo que o pre-commit roda)
python3 scripts/ref-integrity.py --staged
# saída máquina
python3 scripts/ref-integrity.py --range <BASE>..HEAD --json
```

Exit 1 = há referência quebrada; 0 = limpo. Duas checagens: `[link]` (link markdown que não resolve) e
`[stale]` (citação viva a nome/path de arquivo renomeado/deletado no diff).

## O que fazer com cada achado

- **rename limpo** (achado mostra `novo: <path>`) → repontar a citação para o novo path.
- **delete sem novo** (`novo: —`) → desativar o link (manter o texto + nota "histórico no git") ou remover
  o ponteiro em comentário; NUNCA repontar para um doc diferente (link enganoso).
- **falso-positivo conhecido** (auto-output de gerador, backup manual, stray histórico) → adicionar o termo
  em `.ref-integrity-allowlist` (1 por linha) com comentário do porquê.

## Fontes isentas (por design, não reportadas)

`docs/_arquivo/`, `docs/adr/`, `docs/auditorias/`, `docs/qa-evidence/` (snapshots/imutáveis), `**/log.md`
(append-only), `apps/.understand-anything/` e `.trash-*` (scratch). São registro histórico: citação a nome
antigo ali é legítima.

## Guardrail

O pre-commit é fail-fast bypassável (`--no-verify`); o loop `--since` é o backstop. Não é substituto de
revisão — é o guard determinístico que impede rename deixar ref órfã entrar no repo.
