#!/usr/bin/env python3
"""Compatibilidade: o lint canônico agora é repo-wide.

Use `python3 scripts/docs-wiki-lint.py --scope design-system`.
Este wrapper existe para chamadas antigas durante a migração.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    return subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "docs-wiki-lint.py"), "--scope", "design-system"],
        cwd=ROOT,
    )


if __name__ == "__main__":
    sys.exit(main())
