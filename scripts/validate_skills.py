#!/usr/bin/env python3
"""Self-contained validation for Agent Swarm skills and agent metadata."""

from __future__ import annotations

import pathlib
import sys
import tomllib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".agents" / "skills"
REQUIRED_SKILLS = ("learnhouse-delivery-council", "adversarial-review", "clarification-plan")


def fail(message: str) -> None:
    raise SystemExit(message)


def parse_frontmatter(path: pathlib.Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        fail(f"{path.relative_to(ROOT)}: unterminated YAML frontmatter")
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def validate_skill(name: str) -> None:
    folder = SKILL_DIR / name
    if not folder.is_dir():
        fail(f"missing skill folder: {folder.relative_to(ROOT)}")
    metadata = parse_frontmatter(folder / "SKILL.md")
    if metadata.get("name") != name:
        fail(f"{folder.relative_to(ROOT)}/SKILL.md: name must be {name}")
    if not metadata.get("description"):
        fail(f"{folder.relative_to(ROOT)}/SKILL.md: description is required")


def validate_openai_yaml() -> None:
    path = SKILL_DIR / "learnhouse-delivery-council" / "agents" / "openai.yaml"
    text = path.read_text(encoding="utf-8")
    for marker in ("interface:", "display_name:", "short_description:", "default_prompt:"):
        if marker not in text:
            fail(f"{path.relative_to(ROOT)}: missing {marker}")


def validate_toml() -> None:
    tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
    for path in sorted((ROOT / ".codex" / "agents").glob("*.toml")):
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        for field in ("name", "description", "sandbox_mode", "developer_instructions"):
            if field not in data:
                fail(f"{path.relative_to(ROOT)}: missing {field}")


def main() -> int:
    for skill in REQUIRED_SKILLS:
        validate_skill(skill)
    validate_openai_yaml()
    validate_toml()
    print("skill-contract-ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except tomllib.TOMLDecodeError as exc:
        sys.stderr.write(f"TOML parse error: {exc}\n")
        raise SystemExit(1)
