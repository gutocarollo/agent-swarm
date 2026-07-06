# Agent Swarm

Pacote Codex-native do **LearnHouse Delivery Council**: uma skill
orquestradora, skills de apoio, custom agents e um contrato textual de
parametros para escolher onde o agente entra no fluxo.

O objetivo e simples:

1. Ter uma ordem fixa: `PLAN -> PLAN_REVIEW -> EXECUTION -> EXECUTION_REVIEW`.
2. Permitir que `START_AT` escolha a primeira etapa executada nessa ordem.
3. Comecar direto na execucao, no planejamento ou no review de um plano pronto.
4. Tomar decisoes automaticamente quando os trade-offs forem suficientes.
5. Revisar adversarialmente o plano ate 2 vezes quando houver plano.
6. Revisar adversarialmente a execucao ate 3 vezes, corrigindo gaps criticos.

## Estrutura

```text
agent-swarm/
├─ .agents/skills/
│  ├─ learnhouse-delivery-council/
│  ├─ adversarial-review/
│  └─ clarification-plan/
├─ .codex/
│  ├─ config.toml
│  └─ agents/
│     ├─ learnhouse-context-scout.toml
│     ├─ learnhouse-implementer.toml
│     ├─ learnhouse-adversarial-reviewer.toml
│     └─ learnhouse-test-auditor.toml
├─ AGENTS.md
├─ README.md
└─ docs/PLANO-SWARM.md
```

## Parametros

Os argumentos sao passados em texto no prompt. Eles nao sao parametros formais
de funcao do runtime Codex.

```text
Use $learnhouse-delivery-council.

ARGS:
START_AT=EXECUTION | PLANNING | PLAN_REVIEW | AUTO
PLAN_SOURCE=<path | inline | issue | diff>
AUTO_DECIDE=true | false
PLAN_REVIEW_MAX=2
EXECUTION_REVIEW_MAX=3
AUTO_EXECUTE_AFTER_PLAN=false | true

TASK:
[pedido]
```

| Parametro | Default | Regra |
|---|---:|---|
| `START_AT` | `AUTO` | Escolhe a primeira etapa executada na ordem fixa. |
| `PLAN_SOURCE` | omitido | Obrigatorio em `PLAN_REVIEW` se o plano nao estiver colado no prompt. |
| `AUTO_DECIDE` | `true` | Escolhe por trade-off quando nao houver decisao humana real. |
| `PLAN_REVIEW_MAX` | `2` | Limite do loop adversarial do plano. Nao aumentar. |
| `EXECUTION_REVIEW_MAX` | `3` | Limite do loop adversarial da execucao. Nao aumentar. |
| `AUTO_EXECUTE_AFTER_PLAN` | depende | `false` em `PLANNING`; `true` em `PLAN_REVIEW`. |

## Modos

| `START_AT` | Primeira etapa executada | Etapas anteriores |
|---|---|---|
| `PLANNING` | `PLAN` | Nenhuma. O agente cria/estrutura o plano. |
| `PLAN_REVIEW` | `PLAN_REVIEW` | `PLAN` ja existe via `PLAN_SOURCE` ou bloco `PLAN`. |
| `EXECUTION` | `EXECUTION` | `PLAN` e `PLAN_REVIEW` sao assumidos como resolvidos ou desnecessarios para esse chamado. |
| `AUTO` | Inferida | O agente normaliza para `PLANNING`, `PLAN_REVIEW` ou `EXECUTION`. |

## Fluxo Principal

Este e o fluxo que importa. A ordem nao muda: `PLAN_REVIEW` vem depois de
`PLAN`, e `EXECUTION` vem depois de `PLAN_REVIEW`. `START_AT` apenas escolhe
onde entrar nessa sequencia.

```mermaid
flowchart TD
    A["Prompt + ARGS"] --> B["Resolver START_AT<br/>(AUTO vira PLANNING, PLAN_REVIEW ou EXECUTION)"]

    B --> G1{"1. Rodar PLAN?"}
    G1 -->|"sim<br/>START_AT=PLANNING"| P0["PLAN<br/>Criar ou estruturar plano"]
    G1 -->|"nao<br/>PLAN_REVIEW ou EXECUTION"| P1["Plano ja existe<br/>ou etapa ja resolvida"]
    P0 --> G2
    P1 --> G2

    G2{"2. Rodar PLAN_REVIEW?"}
    G2 -->|"sim<br/>PLANNING ou PLAN_REVIEW"| P2["PLAN_REVIEW<br/>review adversarial do plano<br/>rodada i = 1"]
    G2 -->|"nao<br/>START_AT=EXECUTION"| P_SKIP["Plan review assumido<br/>resolvido/desnecessario"]
    P2 --> P3{"PLAN-ADVERSARIAL<br/>status"}
    P3 -->|"REPLANEJAR<br/>i < PLAN_REVIEW_MAX"| P4["Corrigir plano<br/>i = i + 1"]
    P4 --> P2
    P3 -->|"REPLANEJAR<br/>i = PLAN_REVIEW_MAX"| PEND["PENDENTE:<br/>limite do plano atingido"]
    P3 -->|"BLOQUEADO"| PBLOCK["BLOQUEADO:<br/>precisa decisao/evidencia"]
    P3 -->|"SATISFEITO"| G3
    P_SKIP --> G3

    G3{"3. Rodar EXECUTION?"}
    G3 -->|"nao<br/>PLANNING default ou review-only"| PLANOUT["Finalizar com plano revisado"]
    G3 -->|"sim<br/>EXECUTION, PLAN_REVIEW default<br/>ou AUTO_EXECUTE_AFTER_PLAN=true"| X["EXECUTION<br/>Contexto minimo + reuso local"]

    X --> D{"D[n] humano bloqueante?"}
    D -->|"sim"| DBLOCK["BLOQUEADO:<br/>pedir decisao"]
    D -->|"nao"| E["Implementar passo sequencial"]
    E --> F["Validar com comandos reais"]
    F --> G["Review adversarial da execucao<br/>rodada j = 1"]

    G --> H{"ADVERSARIAL<br/>status"}
    H -->|"CORRIGIR<br/>j < EXECUTION_REVIEW_MAX"| I["Corrigir gap REAL<br/>BLOQUEANTE/ALTA<br/>j = j + 1"]
    I --> F
    H -->|"CORRIGIR<br/>j = EXECUTION_REVIEW_MAX"| EPEND["PENDENTE:<br/>limite da execucao atingido"]
    H -->|"BLOQUEADO"| EBLOCK["BLOQUEADO:<br/>decisao, credencial, prod ou acao destrutiva"]
    H -->|"SATISFEITO"| OK["Finalizar:<br/>entrega validada"]
```

## Exemplos De Uso

### Comecar direto na execucao

```text
Use $learnhouse-delivery-council.

ARGS:
START_AT=EXECUTION
AUTO_DECIDE=true
EXECUTION_REVIEW_MAX=3

TASK:
[descreva a implementacao]
```

### Comecar no planejamento

```text
Use $learnhouse-delivery-council.

ARGS:
START_AT=PLANNING
AUTO_DECIDE=true
PLAN_REVIEW_MAX=2
AUTO_EXECUTE_AFTER_PLAN=false

TASK:
[descreva o problema]
```

### Comecar no review de um plano existente

```text
Use $learnhouse-delivery-council.

ARGS:
START_AT=PLAN_REVIEW
PLAN_SOURCE=docs/design-system/sources/MEU-PLANO.md
AUTO_DECIDE=true
PLAN_REVIEW_MAX=2
EXECUTION_REVIEW_MAX=3
AUTO_EXECUTE_AFTER_PLAN=true

TASK:
Revise o plano existente, execute e revise adversarialmente a execucao.
```

Para plano colado no prompt:

```text
ARGS:
START_AT=PLAN_REVIEW
PLAN_SOURCE=inline

PLAN:
[cole o plano aqui]
```

Para apenas revisar o plano sem executar:

```text
ARGS:
START_AT=PLAN_REVIEW
PLAN_SOURCE=docs/design-system/sources/MEU-PLANO.md
AUTO_EXECUTE_AFTER_PLAN=false
```

## Sentinels Obrigatorios

Review do plano:

```md
PLAN-ADVERSARIAL-VERIFICATION: SATISFEITO | REPLANEJAR | BLOQUEADO
GAPS-CRITICOS: N
DECISAO-ESCOLHIDA: [opcao escolhida ou bloqueio]
PROXIMA-ACAO: [executar | replanejar | pedir decisao]
```

Review da execucao:

```md
ADVERSARIAL-VERIFICATION: SATISFEITO | CORRIGIR | BLOQUEADO
GAPS-CRITICOS: N
PROXIMA-ACAO: [corrigir | parar | pedir decisao]
```

Resumo final esperado:

```md
PLAN-ADVERSARIAL-LOOP: <rodadas>/2, status: <SATISFEITO|PENDENTE|BLOQUEADO>
ADVERSARIAL-LOOP: <rodadas>/3, status: <SATISFEITO|PENDENTE|BLOQUEADO>
```

## Arquivos Principais

| Arquivo | Funcao |
|---|---|
| `.agents/skills/learnhouse-delivery-council/SKILL.md` | Skill orquestradora e contrato dos modos. |
| `.agents/skills/adversarial-review/SKILL.md` | Auditoria adversarial com evidencia. |
| `.agents/skills/clarification-plan/SKILL.md` | Decisoes humanas D[n]. |
| `.codex/agents/learnhouse-adversarial-reviewer.toml` | Reviewer read-only com sentinels. |
| `.codex/agents/learnhouse-context-scout.toml` | Scout read-only de contexto. |
| `.codex/agents/learnhouse-implementer.toml` | Implementador workspace-write. |
| `.codex/agents/learnhouse-test-auditor.toml` | Auditor read-only de validacao. |
| `.codex/config.toml` | Limites de project docs e fan-out. |

## Validacao

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

## Manutencao

- Se mudar parametro, atualize a tabela e o fluxo principal.
- Se mudar limite de loop, atualize os ramos `i < PLAN_REVIEW_MAX` e
  `j < EXECUTION_REVIEW_MAX`.
- Se mudar sentinel, atualize a skill e o reviewer TOML.
- Nao publique segredos, `.claude/`, logs, dumps ou detalhes privados de
  cliente neste repositorio.
