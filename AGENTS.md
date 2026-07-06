# Agent Swarm Repo Instructions

Este repositorio publica o pacote Codex-native do LearnHouse Delivery Council.

## Regras De Manutencao

- Mantenha `README.md`, `.agents/skills/learnhouse-delivery-council/SKILL.md`,
  `.codex/agents/learnhouse-adversarial-reviewer.toml` e
  `.agents/skills/learnhouse-delivery-council/agents/openai.yaml` sincronizados
  quando alterar parametros, sentinels ou limites de loop.
- Nao copie `.claude/CLAUDE.md`, credenciais, dumps, logs, dados de producao ou
  instrucoes privadas de cliente para este repo.
- Preserve o repo como pacote autocontido: skill orquestradora, skills de apoio,
  custom agents, config e documentacao.
- Use `rg` para localizar contratos antes de editar.

## Validacao Antes De Commit

Rode:

```bash
python3 /home/augusto/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/learnhouse-delivery-council
python3 /home/augusto/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/adversarial-review
python3 /home/augusto/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/clarification-plan
python3 - <<'PY'
import pathlib
import tomllib
import yaml

for path in pathlib.Path(".codex/agents").glob("*.toml"):
    tomllib.loads(path.read_text())
tomllib.loads(pathlib.Path(".codex/config.toml").read_text())
yaml.safe_load(pathlib.Path(".agents/skills/learnhouse-delivery-council/agents/openai.yaml").read_text())
print("parse-ok")
PY
git diff --check
```

Se a mudanca alterar comportamento do agente, rode tambem uma revisao
adversarial read-only do contrato.
