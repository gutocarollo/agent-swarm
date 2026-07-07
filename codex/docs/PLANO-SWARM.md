> **Documento historico. Nao use como contrato operacional atual.**
>
> O contrato canonico esta em `README.md` e
> `.agents/skills/learnhouse-delivery-council/SKILL.md`.
> Este arquivo preserva a decisao inicial Codex-native. Se houver divergencia,
> o README e a skill vencem. Exemplos copiaveis de loop devem preservar os
> gates atuais `REPLAN-REQUEST`/`REPLAN-CONSUMED` e
> `FIX-REQUEST`/`FIX-CONSUMED`.

Sim — **isso adapta bastante o plano**. A restrição “quero usar dentro da extensão Codex no VS Code, logado com minha assinatura ChatGPT Pro, sem API token” muda a resposta para:

## Não, o Agents SDK não deve ser o caminho principal para o seu caso

O caminho principal deve ser **Codex-native**, usando:

```text
VS Code Codex Extension
  + ChatGPT login / assinatura Pro
  + AGENTS.md
  + repo skills em .agents/skills
  + custom agents em .codex/agents
  + prompts/playbooks explícitos
  + talvez MCP local/docs, se necessário
```

O **Agents SDK** é útil para orquestração programática externa, automação, CI, runners próprios, traces/evals e pipelines que você executa como código Python. Mas ele parte do mundo de **API key/OpenAI Platform**: o quickstart oficial manda configurar `OPENAI_API_KEY`, e a própria documentação diz que o SDK usa a Responses API por padrão para modelos OpenAI. ([OpenAI GitHub][1]) ([OpenAI GitHub][2])

Já a extensão Codex no VS Code suporta login via ChatGPT e está incluída nos planos ChatGPT Plus, Pro, Business, Edu e Enterprise. A documentação oficial também diz que o Codex CLI e a IDE extension suportam tanto login com ChatGPT quanto API key; quando você usa API key, a cobrança passa a ser pela conta OpenAI Platform, não pelos créditos/limites incluídos no plano ChatGPT. ([OpenAI Developers][3]) ([OpenAI Developers][4])

Então: **para você, Agents SDK vira “opcional futuro”, não a base.**

---

## O que eu não tinha deixado claro o suficiente

Não estava claro o suficiente no meu plano anterior que você queria **ficar 100% dentro da extensão Codex no VS Code e usar sua assinatura ChatGPT Pro**, sem API tokens.

Eu mencionei Agents SDK porque ele é a resposta correta para “orquestrar multiagentes programaticamente”. Mas para “quero algo que apareça/funcione como agent ou skill dentro do Codex no VS Code”, a resposta muda:

```text
Antes:
Agents SDK + Codex MCP como orquestrador principal

Agora:
Codex Extension + Skills + Custom Agents + AGENTS.md como orquestrador operacional
```

A parte Agents SDK/MCP só entra depois, caso você queira automação fora da IDE.

---

# Plano adaptado: LearnHouse Codex-native Council

A nova arquitetura fica assim:

```text
/home/augusto/code/learnhouse
  ├─ AGENTS.md
  ├─ .agents/
  │   └─ skills/
  │      ├─ clarification-plan/
  │      │  └─ SKILL.md
  │      ├─ adversarial-review/
  │      │  └─ SKILL.md
  │      └─ learnhouse-delivery-council/
  │         └─ SKILL.md
  └─ .codex/
      ├─ config.toml
      └─ agents/
         ├─ learnhouse-context-scout.toml
         ├─ learnhouse-implementer.toml
         ├─ learnhouse-adversarial-reviewer.toml
         └─ learnhouse-test-auditor.toml
```

A extensão Codex usa o mesmo agente e compartilha configuração com o Codex CLI, segundo a documentação da IDE extension. ([OpenAI Developers][5]) Isso é importante: o que você colocar em `AGENTS.md`, `.agents/skills` e `.codex/agents` deve virar a base de comportamento também no VS Code.

---

# O que vira Skill e o que vira Agent

## Use **Skill** para workflow obrigatório

Skill é o melhor formato para capturar uma rotina reutilizável. A documentação do Codex diz que skills estão disponíveis no CLI, IDE extension e app; podem ser chamadas explicitamente com `$skill` ou escolhidas implicitamente pela descrição; e ficam em diretórios com `SKILL.md`. ([OpenAI Developers][6])

Para o LearnHouse, eu faria três skills:

```text
$clarification-plan
$adversarial-review
$learnhouse-delivery-council
```

Sua skill `adversarial-review` já é o núcleo do controle de qualidade: ela exige confrontar plano, execução, docs de arquitetura, docs de design-system e código real do app, em vez de revisar só o diff.

## Use **Custom Agent** para persona especializada

Custom agent é melhor quando você quer um subagente com papel, sandbox e instruções próprias: explorer read-only, reviewer read-only, implementer workspace-write etc. A documentação do Codex permite definir custom agents em `~/.codex/agents/` ou `.codex/agents/`, com `name`, `description` e `developer_instructions`; também dá para configurar `sandbox_mode`, modelo, MCP e skills. ([OpenAI Developers][7])

Para você:

```text
Skill = processo
Agent = executor especializado
AGENTS.md = constituição permanente do projeto
Prompt = gatilho da rodada
```

---

# Atenção: subagents no VS Code ainda têm uma nuance

Codex já tem subagent workflows habilitados por padrão, mas a documentação diz que a atividade de subagents atualmente é exibida no Codex app e CLI, enquanto a visibilidade na IDE extension está “coming soon”. Ela também diz que Codex só spawna subagents quando você pede explicitamente. ([OpenAI Developers][7])

Tradução prática:

```text
Funciona bem usar skills no VS Code agora.
Funciona bem usar custom agents como configuração do Codex.
Mas não aposte o MVP inteiro em uma UI perfeita de subagents dentro do VS Code.
```

No VS Code, o fluxo mais confiável é: **skill orquestradora + prompts explícitos + agents customizados quando disponíveis**. Para paralelismo pesado e inspeção de subthreads, o CLI/app pode ser melhor até a IDE expor tudo.

---

# Plano correto para seu uso real

## Fase 1 — Login e modo de uso

No VS Code, use a extensão Codex logada com ChatGPT. Isso usa sua assinatura ChatGPT/Codex, não API key. O plano Pro inclui mais uso de Codex que Plus; a página de pricing diz que Pro oferece 5x ou 20x mais uso de Codex que Plus, dependendo do tier. ([OpenAI Developers][8])

Evite colocar `OPENAI_API_KEY` nesse fluxo. API key é outro modo de autenticação e cobrança. ([OpenAI Developers][4])

## Fase 2 — Criar skills repo-scoped

No root do LearnHouse:

```bash
mkdir -p .agents/skills/clarification-plan
mkdir -p .agents/skills/adversarial-review
mkdir -p .agents/skills/learnhouse-delivery-council
```

A documentação diz que, para repositórios, o Codex escaneia `.agents/skills` do diretório atual até o root do repo. Portanto, colocar no root do LearnHouse torna as skills disponíveis para qualquer subpasta do projeto. ([OpenAI Developers][6])

Copie:

```text
.agents/skills/clarification-plan/SKILL.md
.agents/skills/adversarial-review/SKILL.md
```

E crie:

```text
.agents/skills/learnhouse-delivery-council/SKILL.md
```

Essa terceira skill não deve ser gigante; ela só coordena o fluxo.

Exemplo:

```md
---
name: learnhouse-delivery-council
description: Use em tarefas complexas do LearnHouse que envolvam implementação, arquitetura, design-system, banco, auth, tenancy, segurança, testes, PR review ou qualquer mudança que precise de context scout, clarification plan, implementação, validação e adversarial review.
---

# LearnHouse Delivery Council

Você coordena uma entrega dentro de `/home/augusto/code/learnhouse`.

## Fluxo obrigatório

1. Produza um Context Brief antes de implementar.
2. Procure reuso local antes de criar código novo.
3. Se houver decisão técnica aberta, use `$clarification-plan`.
4. Só implemente depois de resolver decisões bloqueantes.
5. Valide com comandos reais.
6. Depois da implementação, use `$adversarial-review`.
7. Não declare feito sem evidência.

## Fontes obrigatórias

- `AGENTS.md`
- `docs/architecture/README.md`
- docs relevantes em `docs/architecture`
- `docs/design-system/index.md` quando houver UI
- docs relevantes em `docs/design-system`
- código real em `apps/api`, `apps/web`, `packages`, migrations e testes

## Saída mínima

- Context Brief
- Plano de implementação
- Arquivos previstos
- Comandos de validação
- Relatório de execução
- Review adversarial
- Pendências reais
```

## Fase 3 — Criar `AGENTS.md`

Esse arquivo é mais importante que o Agents SDK no seu caso.

A documentação diz que Codex lê `AGENTS.md` antes de trabalhar e monta uma cadeia de instruções por escopo global/projeto/diretório. ([OpenAI Developers][9]) Então ele vira a “constituição” do LearnHouse.

Exemplo enxuto:

```md
# LearnHouse Codex Instructions

## Projeto

Você está trabalhando em `/home/augusto/code/learnhouse`.

## Antes de implementar

- Nunca implemente tarefa complexa sem Context Brief.
- Para arquitetura, leia primeiro `docs/architecture/README.md`.
- Para UI/design-system, leia primeiro `docs/design-system/index.md`.
- Procure reuso local com `rg` antes de criar abstração nova.
- Prefira componentes, serviços, hooks, scripts, ADRs e padrões existentes.
- Se houver mais de uma solução razoável, use `$clarification-plan`.

## Implementação

- Faça mudanças pequenas e rastreáveis.
- Não adicione dependência de produção sem justificar.
- Não altere auth, tenancy, dados, migration, billing ou segurança sem revisar docs de arquitetura.
- Não altere UI sem revisar docs do design-system.
- Rode validação mínima relevante antes de concluir.

## Review

- Use `$adversarial-review` após implementação de qualquer tarefa com risco médio/alto.
- O review deve confrontar plano, execução, docs, código real e testes.
- Claim visual exige evidência renderizada.
- Claim de dado exige query ou prova real.
- Não declare “feito” sem comandos e resultados.
```

## Fase 4 — Criar custom agents do Codex

Crie:

```bash
mkdir -p .codex/agents
```

### `.codex/agents/learnhouse-context-scout.toml`

```toml
name = "learnhouse-context-scout"
description = "Read-only explorer for LearnHouse tasks. Use before implementation to map architecture, design-system, local patterns, reusable code, risks, and tests."
sandbox_mode = "read-only"
model_reasoning_effort = "medium"

developer_instructions = """
You are LearnHouse Context Scout.

Do not edit files.

Before any implementation, produce a Context Brief:
- relevant architecture docs
- relevant design-system docs
- existing local patterns
- reusable components/services/hooks/scripts
- likely files to change
- tests and validation commands
- risks and open decisions

Prioritize targeted searches with rg and focused file reads.
"""
```

### `.codex/agents/learnhouse-implementer.toml`

```toml
name = "learnhouse-implementer"
description = "Implementation-focused LearnHouse agent. Use only after context and clarification gates are resolved."
sandbox_mode = "workspace-write"
model_reasoning_effort = "medium"

developer_instructions = """
You implement only the approved plan.

Rules:
- Do not implement unresolved D[n] decisions.
- Reuse existing patterns before creating new abstractions.
- Keep diffs small.
- Run targeted validation.
- Return changed files, commands run, results, and remaining risks.
"""
```

### `.codex/agents/learnhouse-adversarial-reviewer.toml`

```toml
name = "learnhouse-adversarial-reviewer"
description = "Read-only adversarial reviewer for LearnHouse plans, diffs, PRs, architecture, design-system, tests, and execution evidence."
sandbox_mode = "read-only"
model_reasoning_effort = "high"

developer_instructions = """
You are the LearnHouse adversarial reviewer.

Always use $adversarial-review when available.

You must compare:
1. Original request or plan.
2. Actual execution and git diff.
3. docs/architecture contracts.
4. docs/design-system contracts.
5. Real app code and tests.

Do not edit files.
Do not invent evidence.
Every finding must be proven or refuted.
"""
```

### `.codex/agents/learnhouse-test-auditor.toml`

```toml
name = "learnhouse-test-auditor"
description = "Read-only validation auditor for LearnHouse. Checks whether tests, build, lint, typecheck, DB evidence, and UI evidence actually support the implementation claims."
sandbox_mode = "read-only"
model_reasoning_effort = "medium"

developer_instructions = """
You audit validation evidence.

Check:
- commands actually run
- logs/results
- tests cover changed behavior
- UI evidence exists when visual claims matter
- DB/query evidence exists when data claims matter
- no 'done' claim without proof

Do not edit files.
"""
```

## Fase 5 — Configurar `.codex/config.toml`

```toml
[agents]
max_threads = 4
max_depth = 1
```

Eu manteria `max_depth = 1`. A documentação alerta que aumentar profundidade pode gerar fan-out recursivo, mais custo, mais latência e menos previsibilidade. ([OpenAI Developers][7])

---

# Como usar no VS Code

## Para começar uma feature

No chat da extensão Codex:

```text
Use $learnhouse-delivery-council.

ARGS:
START_AT=AUTO
AUTO_DECIDE=true
PLAN_REVIEW_MAX=2
EXECUTION_REVIEW_MAX=3
AUTO_EXECUTE_AFTER_PLAN=false

Tarefa:
[descreva a feature]

Trabalhe em fases:
1. Faça Context Brief.
2. Aponte reuso local obrigatório.
3. Se houver alternativas, escolha automaticamente a melhor por trade-off quando AUTO_DECIDE=true.
4. Use $clarification-plan apenas se sobrar decisão D[n] realmente bloqueante.
5. Não implemente decisão D[n] aberta; se START_AT=PLANNING, só implemente depois do plano se AUTO_EXECUTE_AFTER_PLAN=true.
6. Se START_AT=PLAN_REVIEW, o plano já existe: revise o plano, execute apenas quando `PLAN-ADVERSARIAL-VERIFICATION: SATISFEITO` e rode review adversarial da execução. Não refaça o planejamento inicial amplo.
7. Se o review do plano retornar REPLANEJAR, exija REPLAN-REQUEST, consuma em REPLAN-CONSUMED e rode novo PLAN_REVIEW antes de executar.
8. Se o review da execução retornar CORRIGIR, exija FIX-REQUEST, corrija em FIX-CONSUMED, revalide e rode novo review da execução antes de SATISFEITO.
```

Limites fixos:

- `PLAN_REVIEW_MAX` não passa de 2.
- `EXECUTION_REVIEW_MAX` não passa de 3.

## Para começar direto na execução

```text
Use $learnhouse-delivery-council.

ARGS:
START_AT=EXECUTION
AUTO_DECIDE=true
EXECUTION_REVIEW_MAX=3

TASK:
[descreva a implementação]
```

## Para começar no planejamento

```text
Use $learnhouse-delivery-council.

ARGS:
START_AT=PLANNING
AUTO_DECIDE=true
PLAN_REVIEW_MAX=2
AUTO_EXECUTE_AFTER_PLAN=false

TASK:
[descreva o problema/feature]
```

## Para começar no review de um plano existente

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
Revise o plano existente, execute apenas se PLAN-ADVERSARIAL-VERIFICATION ficar SATISFEITO e rode review adversarial da execução.
Se o review retornar REPLANEJAR, devolva REPLAN-REQUEST, consuma em REPLAN-CONSUMED e rode novo PLAN_REVIEW.
```

Se o plano estiver colado no prompt, use `PLAN_SOURCE=inline` e adicione:

```text
PLAN:
[cole o plano aqui]
```

Para apenas revisar o plano sem executar, mantenha `START_AT=PLAN_REVIEW` e defina `AUTO_EXECUTE_AFTER_PLAN=false`.

## Para implementar após aprovar o plano

```text
Com base no plano aprovado, implemente.

Use learnhouse-implementer se custom agents estiverem disponíveis.
Mantenha escopo mínimo.
Rode validação específica.
Ao final, entregue:
- arquivos alterados
- comandos rodados
- resultado dos comandos
- riscos restantes
```

## Para review adversarial

```text
Use $adversarial-review.

Revise esta branch/diff contra o plano aprovado.
Confronte:
- plano
- execução
- docs/architecture
- docs/design-system
- código real
- testes/evidências

Não edite arquivos.
Classifique achados como REAL, REFUTADO, TEORICO-descartado ou NAO-PROVADO.
```

## Para conclusão com Adversarial Verification Loop

```text
Ao terminar a implementação, rode o Adversarial Verification Loop.

Regras:
1. Rode $adversarial-review ou learnhouse-adversarial-reviewer contra plano, diff, docs, código real e evidências.
2. Se houver gap REAL BLOQUEANTE ou ALTA que possa ser corrigido sem decisão humana, o reviewer deve retornar FIX-REQUEST.
3. O Council corrige consumindo o FIX-REQUEST, registra FIX-CONSUMED, revalida e só então roda nova rodada adversarial.
4. Repita até o review declarar SATISFEITO ou até completar 3 rodadas.
5. Pare e declare BLOQUEADO se sobrar decisão D[n], credencial, acesso externo, prod/deploy ou ação destrutiva.
6. Declare PENDENTE se a rodada 3 ainda retornar CORRIGIR; nesse caso não declare ADVERSARIAL-VERIFICATION: SATISFEITO.

Saída obrigatória:
ADVERSARIAL-LOOP: <rodadas>/3, status: <SATISFEITO|PENDENTE|BLOQUEADO>
FIX-REQUEST: [obrigatorio quando status da rodada for CORRIGIR]
FIX-CONSUMED: [obrigatorio antes da rodada seguinte quando houve CORRIGIR]
```

## Para swarm/subagents quando fizer sentido

```text
Investigue esta tarefa com subagents.

Spawn:
1. learnhouse-context-scout para mapear arquitetura e padrões locais.
2. learnhouse-adversarial-reviewer para antecipar riscos do plano.
3. learnhouse-test-auditor para mapear validações necessárias.

Espere todos terminarem e consolide:
- riscos reais
- decisões D[n]
- plano recomendado
```

Só usaria isso para tarefas complexas, porque subagents consomem mais tokens/limite; a documentação do Codex avisa que cada subagent faz seu próprio trabalho de modelo e ferramentas. ([OpenAI Developers][7])

---

# O que sai do plano anterior

Eu removeria do MVP:

```text
scripts/learnhouse_delivery_council.py
Agents SDK
Codex MCP server
Runner.run(...)
trace(...)
guardrails em Python
pipeline externo
```

Essas peças só voltam depois se você quiser:

```text
- rodar fora do VS Code
- automatizar CI
- criar bot de PR
- gerar traces/evals programáticos
- orquestrar Codex como ferramenta de outro agente
- usar API Platform e pagar por token
```

O MCP server do Codex com Agents SDK continua existindo oficialmente, mas é um caminho para “invocar Codex como MCP server a partir de outro cliente/agente”, não para operar naturalmente dentro da extensão Codex com assinatura ChatGPT. ([OpenAI Developers][10])

---

# Decisão revisada

### D1 — Para o seu objetivo, qual runtime usar?

**Opção A — Agents SDK externo**

* **Comportamento:** você cria um programa Python que orquestra agentes e chama modelos via API.
* **Exemplo aplicado bom:** um CI roda todo PR do LearnHouse, chama reviewer, test auditor, repair loop e grava traces.
* **Exemplo aplicado ruim:** você precisa de API key e cobrança OpenAI Platform; isso foge do seu requisito de usar apenas a assinatura ChatGPT Pro.
* **Quando escolher:** só quando você quiser automação externa ao VS Code.

**Opção B — Codex-native dentro da extensão**

* **Comportamento:** você trabalha no VS Code com Codex logado via ChatGPT, usando `AGENTS.md`, `.agents/skills`, `.codex/agents` e prompts.
* **Exemplo aplicado bom:** você digita `Use $learnhouse-delivery-council` na extensão e o Codex segue seu protocolo de Context Brief → clarificação → implementação → validação → review adversarial.
* **Exemplo aplicado ruim:** você não terá, no MVP, a mesma rastreabilidade programática de um pipeline Agents SDK com traces/evals externos.
* **Quando escolher:** escolha esta. É exatamente o seu requisito.

**Opção C — Codex-native agora + Agents SDK depois**

* **Comportamento:** começa 100% dentro da extensão; quando o workflow estabilizar, você transforma partes em automação externa.
* **Exemplo aplicado bom:** primeiro você prova que `$adversarial-review` pega bugs reais no LearnHouse; depois cria um runner de CI para aplicar o mesmo protocolo.
* **Exemplo aplicado ruim:** se você tentar fazer as duas coisas ao mesmo tempo, aumenta a complexidade antes de validar o processo.
* **Quando escolher:** é o caminho mais seguro de evolução.

---

# Recomendação final adaptada

Para o seu caso, o plano correto é:

```text
1. Usar Codex Extension no VS Code logado com ChatGPT Pro.
2. NÃO usar Agents SDK no MVP.
3. Transformar suas skills em repo skills:
   .agents/skills/clarification-plan/SKILL.md
   .agents/skills/adversarial-review/SKILL.md
   .agents/skills/learnhouse-delivery-council/SKILL.md
4. Criar AGENTS.md no root do LearnHouse.
5. Criar custom agents em .codex/agents para scout, implementer, reviewer e test auditor.
6. Usar prompts explícitos no VS Code para disparar o fluxo.
7. Só considerar Agents SDK depois, para automação fora da IDE.
```

A versão corrigida da frase central do plano seria:

> **Não vamos criar um agente externo com Agents SDK agora. Vamos criar uma camada nativa do Codex para o LearnHouse, composta por AGENTS.md + Skills + Custom Agents, acionável diretamente na extensão Codex do VS Code usando sua assinatura ChatGPT Pro.**

[1]: https://openai.github.io/openai-agents-python/quickstart/
[2]: https://openai.github.io/openai-agents-python/
[3]: https://developers.openai.com/codex/ide
[4]: https://developers.openai.com/codex/auth
[5]: https://developers.openai.com/codex/ide/features
[6]: https://developers.openai.com/codex/skills
[7]: https://developers.openai.com/codex/subagents
[8]: https://developers.openai.com/codex/pricing
[9]: https://developers.openai.com/codex/guides/agents-md
[10]: https://developers.openai.com/codex/guides/agents-sdk
