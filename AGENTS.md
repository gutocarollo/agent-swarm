# Agent Swarm Repo Instructions

Este repositorio publica o pacote Codex-native do LearnHouse Delivery Council.

## Regras De Manutencao

- Mantenha `README.md`, `.agents/skills/learnhouse-delivery-council/SKILL.md`,
  `.codex/agents/learnhouse-adversarial-reviewer.toml` e
  `.agents/skills/learnhouse-delivery-council/agents/openai.yaml` sincronizados
  quando alterar parametros, sentinels ou limites de loop.
- Preserve o gate sequencial: `PLAN -> PLAN_REVIEW -> EXECUTION -> EXECUTION_REVIEW`.
  Execucao so pode seguir de planejamento quando o ultimo `PLAN_REVIEW` retornar
  `SATISFEITO`; `REPLANEJAR` na rodada final e `PENDENTE` real e bloqueia execucao.
- Preserve o handoff de replanejamento: reviewer retorna `REPLAN-REQUEST`;
  Council consome e registra `REPLAN-CONSUMED`; sem esses blocos, o loop e invalido.
- Preserve o handoff de correcao: reviewer retorna `FIX-REQUEST`; Council
  corrige, revalida e registra `FIX-CONSUMED`; sem esses blocos, o loop e invalido.
- Preserve a abstracao de contrato executavel: `scripts/validate_contract.py` e
  o ponto unico de validacao; `scripts/verify_witness.py` apenas verifica
  marcadores load-bearing; `scripts/agent_swarm_ledger.py` apenas registra
  evidencia de rodadas. Nao transforme esses scripts em segundo orquestrador.
- Nao copie `.claude/CLAUDE.md`, credenciais, dumps, logs, dados de producao ou
  instrucoes privadas de cliente para este repo.
- Preserve o repo como pacote autocontido: skill orquestradora, skills de apoio,
  custom agents, config e documentacao.
- Use `rg` para localizar contratos antes de editar.

## Validacao Antes De Commit

Rode:

```bash
python3 scripts/validate_contract.py
```

Se a mudanca alterar comportamento do agente, rode tambem uma revisao
adversarial read-only do contrato.
