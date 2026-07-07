#!/usr/bin/env python3
"""ref-integrity.py — integridade referencial git-aware (renames/deletes).

FONTE ÚNICA (SOLID/DRY) consumida por 3 adaptadores finos:
  - pre-commit git hook  → --staged   (resolve/grep no INDEX; bloqueia o commit)
  - skill invocável      → --range A..B
  - loop scheduled       → --since <ref>

Duas checagens determinísticas:
  (A) broken-md-links   — links markdown `](path)` que não resolvem.
  (B) stale-citations   — citações vivas ao PATH/nome ANTIGO de arquivos renomeados/deletados
                          no git diff do seletor. Reconcilia falso-positivo vs falso-negativo:
                          basename que SUMIU do repo → busca por basename (pega citação sem path);
                          basename que AINDA existe (renomeado) → busca só por PATH completo antigo
                          (não flag `multi-tenancy.md` que resolve para o novo local).

Eixo "onde-buscar" rege AMBAS as checagens: --staged usa o INDEX (git show :path /
git cat-file -e :path / git grep --cached); --range/--since usam o working tree em HEAD.

Dois níveis de isenção:
  - is_archive (check A e B): docs/_arquivo/, apps/.understand-anything/ (+.trash) — arqueologia pura.
  - is_historical (só check B / stale-citation): + docs/adr/, docs/auditorias/, docs/qa-evidence/, **/log.md
    — CITAÇÃO em prosa a nome antigo é snapshot legítimo, mas LINK markdown clicável quebrado ali NÃO é
    isento (check A enforça: o índice não pode ter link morto).
Exceções conhecidas (auto-output de geradores, backup manual): `.ref-integrity-allowlist`.

Exit 1 se houver referência quebrada real; 0 caso contrário. `--json` para saída máquina.
Ver docs/SCHEMA.md §5 ("git é o arquivo") e a skill ref-integrity.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

ALLOW_EXT = {".md", ".json", ".txt", ".py", ".sh", ".toml", ".mjs", ".ts",
             ".tsx", ".css", ".yaml", ".yml", ".snyk"}
GENERIC_BASENAMES = {"index.md", "log.md", "readme.md", "schema.md", "__init__.py",
                     "config.json", "package.json", "utils.py", "types.ts"}
LINK_RE = re.compile(r"\]\(\s*([^)\s]+)")


def sh(args: list[str]) -> str:
    return subprocess.run(args, capture_output=True, text=True).stdout


ROOT = sh(["git", "rev-parse", "--show-toplevel"]).strip()


def load_allowlist() -> set[str]:
    """Termos a ignorar globalmente (auto-output de geradores, backups). 1 por linha; '#' = comentário."""
    p = os.path.join(ROOT, ".ref-integrity-allowlist")
    terms: set[str] = set()
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.split("#", 1)[0].strip()
            if line:
                terms.add(line)
    return terms


def is_archive(path: str) -> bool:
    """Arqueologia pura — nem link clicável precisa resolver (docs mortos/scratch)."""
    p = path.replace("\\", "/")
    return p.startswith("docs/_arquivo/") or ".understand-anything" in p or "/.trash-" in p


def is_historical(path: str) -> bool:
    """Registro histórico/snapshot: CITAÇÃO em prosa a nome antigo é legítima (check B exempta).
    Mas LINK markdown clicável quebrado NÃO é exempto aqui (check A usa is_archive, mais estreito)."""
    p = path.replace("\\", "/")
    if is_archive(p):
        return True
    # ADR imutável (Nygard), auditorias e qa-evidence = snapshots datados; log.md = append-only
    if p.startswith(("docs/adr/", "docs/auditorias/", "docs/qa-evidence/")):
        return True
    if os.path.basename(p) == "log.md":
        return True
    return False


def has_allowed_ext(path: str) -> bool:
    base = os.path.basename(path)
    if base.endswith(".snyk") or base == ".snyk":  # dotfile: splitext dá ext vazia
        return True
    return os.path.splitext(path)[1] in ALLOW_EXT


def tracked_files() -> list[str]:
    return [x for x in sh(["git", "ls-files"]).splitlines() if x]


def exists_in_index(relpath: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f":{relpath}"],
                          capture_output=True).returncode == 0


def path_exists(rel: str, cached: bool) -> bool:
    rel = os.path.normpath(rel)
    if not rel or rel.startswith(".."):
        return False
    return exists_in_index(rel) if cached else os.path.exists(os.path.join(ROOT, rel))


PATH_TOKEN = r"[\w./-]*"


def rd_pairs(diff_args: list[str]) -> list[tuple[str, str | None]]:
    out = sh(["git", "diff", "--name-status", "--diff-filter=RD", *diff_args])
    pairs: list[tuple[str, str | None]] = []
    for line in out.splitlines():
        parts = line.split("\t")
        if not parts or not parts[0]:
            continue
        st = parts[0]
        if st.startswith("R") and len(parts) >= 3:
            pairs.append((parts[1], parts[2]))
        elif st == "D" and len(parts) >= 2:
            pairs.append((parts[1], None))
    return pairs


def git_grep(term: str, cached: bool) -> list[tuple[str, int, str]]:
    # term é o PATTERN (-e); busca no index (--cached) ou no working tree tracked.
    cmd = ["git", "grep", "-n", "-F"] + (["--cached"] if cached else []) + ["-e", term]
    res = subprocess.run(cmd, capture_output=True, text=True)
    hits: list[tuple[str, int, str]] = []
    for line in res.stdout.splitlines():
        m = re.match(r"^(.+?):(\d+):(.*)$", line)
        if m:
            hits.append((m.group(1), int(m.group(2)), m.group(3)))
    return hits


def check_stale_citations(diff_args, cached, tracked_bases, allow) -> list[dict]:
    findings: list[dict] = []
    seen = set()
    for old, new in rd_pairs(diff_args):
        base = os.path.basename(old)
        by_basename = not (base.lower() in GENERIC_BASENAMES or base in tracked_bases)
        term = base if by_basename else old
        if term in allow or base in allow:
            continue
        for f, ln, content in git_grep(term, cached):
            if not has_allowed_ext(f) or is_historical(f) or f == new:
                continue
            # token isolado (não sufixo/prefixo de nome maior, ex. e01-leaderboard.png)
            m2 = re.search(r"(?<![\w-])(" + PATH_TOKEN + re.escape(term) + PATH_TOKEN + r")(?![\w-])", content)
            if not m2:
                continue
            # se o path ao redor do match RESOLVE (foi corrigido p/ novo local, ou é outro arquivo
            # que só contém o nome como substring), não é stale.
            tok = m2.group(1).lstrip("./")
            cands = [os.path.join(os.path.dirname(f), tok), tok]
            if any(path_exists(c, cached) for c in cands):
                continue
            key = (f, ln, term)
            if key in seen:
                continue
            seen.add(key)
            findings.append({"check": "stale-citation", "old": old, "new": new,
                             "term": term, "file": f, "line": ln,
                             "snippet": content.strip()[:120]})
    return findings


def _md_targets(text: str):
    for i, line in enumerate(text.splitlines(), 1):
        for m in LINK_RE.finditer(line):
            tgt = m.group(1).split("#")[0].strip()
            if tgt and not tgt.startswith(("http://", "https://", "mailto:", "#", "<", "tel:")):
                yield i, tgt, line


def check_md_links(staged: bool, allow: set[str]) -> list[dict]:
    findings: list[dict] = []
    if staged:
        files = [f for f in sh(["git", "diff", "--cached", "--name-only",
                                "--diff-filter=ACM"]).splitlines() if f.endswith(".md")]
    else:
        files = [f for f in tracked_files() if f.endswith(".md")]
    for f in files:
        if is_archive(f):  # link clicável quebrado é ruído mesmo em log/auditoria/adr; só _arquivo é isento
            continue
        try:
            text = sh(["git", "show", f":{f}"]) if staged else open(os.path.join(ROOT, f), encoding="utf-8").read()
        except OSError:
            continue
        for ln, tgt, line in _md_targets(text):
            if tgt in allow:
                continue
            # tenta dir-relativo E repo-relativo (docs citam paths repo-relativos sem '/' inicial)
            if tgt.startswith("/"):
                cands = [tgt.lstrip("/")]
            else:
                cands = [os.path.normpath(os.path.join(os.path.dirname(f), tgt)),
                         os.path.normpath(tgt)]
            cands = [c for c in cands if c and not c.startswith("..")]
            ok = any((exists_in_index(c) if staged else os.path.exists(os.path.join(ROOT, c))) for c in cands)
            if not ok:
                findings.append({"check": "broken-md-link", "file": f, "line": ln,
                                 "target": tgt, "snippet": line.strip()[:120]})
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="Integridade referencial git-aware (renames/deletes).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--staged", action="store_true", help="pre-commit: staged + index")
    g.add_argument("--range", metavar="A..B", help="skill: range de commits")
    g.add_argument("--since", metavar="REF", help="loop: REF..HEAD")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    allow = load_allowlist()
    tracked_bases = {os.path.basename(p) for p in tracked_files()}
    findings: list[dict] = []

    if a.staged:
        findings += check_stale_citations(["--cached"], True, tracked_bases, allow)
        findings += check_md_links(staged=True, allow=allow)
    else:
        rng = a.range if a.range else f"{a.since}..HEAD"
        findings += check_stale_citations([rng], False, tracked_bases, allow)
        findings += check_md_links(staged=False, allow=allow)

    # dedup global (A e B podem reportar o mesmo link p/ arquivo deletado)
    uniq, keys = [], set()
    for x in findings:
        k = (x["file"], x["line"], x.get("target") or x.get("term"))
        if k not in keys:
            keys.add(k)
            uniq.append(x)
    findings = uniq

    if a.json:
        print(json.dumps(findings, indent=2, ensure_ascii=False))
    elif not findings:
        print("ref-integrity: OK — nenhuma referência quebrada")
    else:
        print(f"ref-integrity: FAIL — {len(findings)} referência(s) quebrada(s):")
        for x in findings:
            if x["check"] == "broken-md-link":
                print(f"  [link]  {x['file']}:{x['line']} → {x['target']} (não resolve)")
            else:
                print(f"  [stale] {x['file']}:{x['line']} → cita '{x['term']}' (removido; novo: {x['new'] or '—'})")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
