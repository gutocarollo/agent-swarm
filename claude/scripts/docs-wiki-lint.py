#!/usr/bin/env python3
"""Lint da wiki Karpathy do REPOSITÓRIO inteiro (docs/), não só design-system.

Regras (docs/SCHEMA.md):
- FAIL: todo .md não-estrutural precisa estar citado individualmente ou coberto por uma coleção
  explicitamente indexada em algum index.md/log.md/README.md sob docs/.
- FAIL: arquivo não-markdown (json/png/pdf/...) precisa estar citado pelo nome ou coberto por uma coleção
  explicitamente indexada (containers genéricos sources/assets/img/reports não contam).
- WARN: naming de Markdown fora do padrão §2 (kebab-case; event=YYYY-MM-DD-slug; sequenced=NNNN-slug).
  Não bloqueia por default — a migração de nomes é incremental via loop. Use --strict-naming para tornar FAIL.

Uso:
  python3 scripts/docs-wiki-lint.py                 # repo inteiro (docs/)
  python3 scripts/docs-wiki-lint.py --scope design-system   # só uma categoria (usado por gates)
  python3 scripts/docs-wiki-lint.py --strict-naming # naming também bloqueia
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

STRUCTURAL = {"index.md", "log.md", "SCHEMA.md", "README.md"}
CAPS_OK = {"README.md", "SCHEMA.md", "CLAUDE.md", "AGENTS.md", "LICENSE", "LICENSE.md", "PROVENANCE.md"}
GENERIC_DIRS = {"sources", "assets", "img", "images", "reports", "docs", "_arquivo"}
IGNORED_DIRS = {".understand-anything"}
# kebab minúsculo, com prefixo opcional de data (event) ou número (sequenced); ponto só p/ versão tipo v2.2
NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}-|\d+-)?[a-z0-9]+([a-z0-9.\-]*[a-z0-9])?\.[a-z0-9]+$")
# data (YYYY-MM-DD) presente mas NÃO como prefixo → event doc com data em sufixo (§2: deve ser prefixo)
DATE_ANY = re.compile(r"\d{4}-\d{2}-\d{2}")


def collect_index_corpus(scope_dir: Path) -> str:
    """Concatena índices sob docs/ (o topo sempre conta), para checar menção."""
    parts: list[str] = []
    for name in ("index.md", "log.md", "README.md"):
        top = DOCS / name
        if top.exists():
            parts.append(top.read_text(encoding="utf-8"))
    for idx in DOCS.rglob("index.md"):
        parts.append(idx.read_text(encoding="utf-8"))
    for lg in DOCS.rglob("log.md"):
        parts.append(lg.read_text(encoding="utf-8"))
    for readme in DOCS.rglob("README.md"):
        parts.append(readme.read_text(encoding="utf-8"))
    return "\n".join(parts)


def mentioned(rel: Path, corpus: str) -> bool:
    return rel.as_posix() in corpus or rel.name in corpus


def collection_mentioned(rel: Path, corpus: str) -> bool:
    """Aceita cobertura por coleção explícita, sem deixar top-level genérico cobrir tudo."""
    parts = rel.parts[:-1]
    for i in range(len(parts), 1, -1):
        leaf = parts[i - 1]
        if leaf in GENERIC_DIRS:
            continue
        ancestor = "/".join(parts[:i])
        if (
            f"{ancestor}/" in corpus
            or ancestor in corpus
            or f"{leaf}/" in corpus
            or f"`{leaf}`" in corpus
        ):
            return True
    return False


FOREIGN_LIVE_FORBIDDEN = ("_arquivo/",)


def check_no_foreign_live_links(base: Path) -> list[str]:
    """Índice vivo (`index.md`) que linka `_arquivo/`. Padrão portado do slim-shape, onde é FAIL
    (lá o índice nunca aponta para o arquivo). No learnhouse é **WARN**: os índices usam links a
    `_arquivo/` como WAYFINDING rotulado ("históricos/superados/reuniões passadas →" / "prova em"),
    que é prática Karpathy correta — falso-FAIL treinaria o time a ignorar o gate. WARN surfacia
    para o olho humano na curadoria sem quebrar o verde. `log.md` isento (registro do que saiu)."""
    errs: list[str] = []
    for idx in sorted(base.rglob("index.md")):
        if any(part in IGNORED_DIRS for part in idx.relative_to(DOCS).parts):
            continue
        rel = idx.relative_to(DOCS)
        for m in re.finditer(r"\]\(([^)]+)\)", idx.read_text(encoding="utf-8")):
            tgt = m.group(1).split("#")[0].strip().lstrip("./")
            if any(tok in tgt for tok in FOREIGN_LIVE_FORBIDDEN):
                errs.append(f"índice vivo linka fonte arquivada: {rel} -> {m.group(1)}")
    return errs


def naming_ok(rel: Path) -> bool:
    name = rel.name
    if name in CAPS_OK or name in {"index.md", "log.md"}:
        return True
    if not NAME_RE.match(name):
        return False
    # §2: event doc datado deve ter a data em PREFIXO (ordena no ls). Data em sufixo é violação.
    if DATE_ANY.search(name) and not re.match(r"^\d{4}-\d{2}-\d{2}-", name):
        return False
    return True


def main() -> int:
    args = sys.argv[1:]
    strict_naming = "--strict-naming" in args
    scope = None
    if "--scope" in args:
        scope = args[args.index("--scope") + 1]
    base = DOCS / scope if scope else DOCS
    corpus = collect_index_corpus(base)

    failures: list[str] = []
    naming_warns: list[str] = []

    for f in sorted(base.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(DOCS)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        if rel.name in STRUCTURAL and f.suffix == ".md":
            continue
        # cobertura: menção individual ou coleção explicitamente indexada.
        covered = mentioned(rel, corpus) or collection_mentioned(rel, corpus)
        if not covered:
            failures.append(f"órfão (sem menção em index/log): {rel}")
        # naming (§2)
        if f.suffix == ".md" and not naming_ok(rel):
            naming_warns.append(f"naming fora do padrão §2: {rel}")

    foreign_warns = check_no_foreign_live_links(base)

    if strict_naming:
        failures.extend(naming_warns)
        naming_warns = []

    if naming_warns:
        print(f"docs-wiki-lint: {len(naming_warns)} aviso(s) de naming (WARN, migração incremental):")
        for w in naming_warns[:60]:
            print(f"  ~ {w}")
        if len(naming_warns) > 60:
            print(f"  ... +{len(naming_warns) - 60} outros")

    if foreign_warns:
        print(f"docs-wiki-lint: {len(foreign_warns)} índice(s) vivo(s) linkando _arquivo/ (WARN — confira se é wayfinding rotulado):")
        for w in foreign_warns:
            print(f"  ~ {w}")

    if failures:
        print("docs-wiki-lint: FAIL")
        for x in failures:
            print(f"- {x}")
        return 1

    scope_txt = f" (scope={scope})" if scope else ""
    print(f"docs-wiki-lint: OK{scope_txt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
