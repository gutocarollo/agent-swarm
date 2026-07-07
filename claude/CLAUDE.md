# CLAUDE.md — metodologia de padronização e workflow (curado para publicação)

> Extraído do CLAUDE.md de um repositório de cliente em 2026-07-07 e curado para repo PÚBLICO:
> blocos de infra/produção, credenciais e contexto comercial do cliente foram REMOVIDOS.
> Mantidos os blocos de metodologia: wiki Karpathy temporal (repo-wide), council Codex-native
> com adversarial loops por subagent, LEI ZERO (não reinventar), §14 consistência DRY,
> §15 workflow orchestration (Boris Cherny) e §16 self-improvement loop (lessons.md + hooks).

## ⭐ REFERÊNCIA CANÔNICA — Repo Wiki / Documentação = Karpathy temporal

**A wiki Karpathy é do REPOSITÓRIO INTEIRO, não só do design-system.** O objetivo é reduzir erro de agente causado por documento ambíguo, antigo ou lixo misturado com verdade atual.

- **Constituição:** `docs/SCHEMA.md` define naming, status, indexação temporal, ingest/query/lint/prune e política "git é o arquivo".
- **Naming obrigatório para docs novos:** `kebab-case` minúsculo; `living` sem data (`slug.md`), `event` com data-prefixo (`YYYY-MM-DD-slug.md`), `sequenced` numerado (`NNNN-slug.md`). FULL-CAPS/Title-Case são dívida a migrar sequencialmente.
- **Indexação temporal:** todo doc entra no índice da categoria e no `docs/log.md`; coleções coesas podem ser indexadas por diretório explícito + `README.md` interno.
- **Skill:** `repo-wiki-curator` substitui `design-system-wiki-ingest`. Use para qualquer curadoria de `docs/`: planos, auditorias, architecture, commercial, developers, reuniões, qa-evidence e design-system.
- **Guard:** `python3 scripts/docs-wiki-lint.py` é o lint canônico repo-wide; `python3 scripts/docs-wiki-lint.py --scope design-system` é o scope especializado. O script antigo `design-system-wiki-lint.py` é só wrapper de compatibilidade.
- **Loop:** `.claude/loop.md` roda curadoria contínua do repo inteiro. Naming warnings são backlog incremental; órfão sem índice é falha.

## ⭐ REFERÊNCIA CANÔNICA — LearnHouse Codex-native Council

**Para tarefas complexas no LearnHouse, o fluxo operacional canônico no Codex é repo-native: `AGENTS.md` + `.agents/skills` + `.codex/agents` + prompts explícitos. Não usar Agents SDK, Codex MCP server, runner Python, traces/evals programáticos ou `OPENAI_API_KEY` como base do MVP dentro da extensão Codex no VS Code.**

- **Skill orquestradora:** `$learnhouse-delivery-council` em `.agents/skills/learnhouse-delivery-council/SKILL.md`.
- **Skills de apoio:** `$clarification-plan` para decisões D[n] com consequências concretas; `$adversarial-review` para verificar plano × execução × docs × código × testes.
- **Custom agents de subagent:** `.codex/agents/learnhouse-context-scout.toml`, `learnhouse-implementer.toml`, `learnhouse-adversarial-reviewer.toml`, `learnhouse-test-auditor.toml`.
- **Config do projeto:** `.codex/config.toml` mantém `project_doc_max_bytes = 65536` para evitar truncamento da cadeia `~/.codex/AGENTS.md` + `AGENTS.md`, e `[agents] max_threads = 4` / `max_depth = 1` para controlar fan-out. Não aumentar profundidade sem justificativa, porque subagents consomem mais tokens/latência e podem criar fan-out recursivo.

Fluxo mínimo para tarefa de risco médio/alto:

1. Produzir **Context Brief** antes de implementar.
2. Buscar reuso local com `rg` antes de criar abstração nova.
3. Se houver mais de uma solução razoável, comparar trade-offs e escolher automaticamente quando `AUTO_DECIDE=true`; usar `$clarification-plan` apenas para decisão humana D[n] realmente bloqueante.
4. Implementar em passos pequenos e sequenciais, preservando mudanças locais não relacionadas.
5. Validar com comandos reais; claim visual exige evidência renderizada e claim de dado exige query/prova real.
6. Rodar o **Adversarial Verification Loop** ao final.

**Adversarial Verification Loop (obrigatório para risco médio/alto):**

- Disparar um SUBAGENT `learnhouse-adversarial-reviewer` (Claude: Agent tool; Codex: custom agent thread) contra plano, diff, docs, código real e evidências. Review adversarial NUNCA roda inline no contexto principal — self-review de quem produziu o diff não é adversarial e as leituras estouram o contexto; `$adversarial-review` é o CONTRATO do prompt do subagent. Rodada N+1 pode continuar o MESMO subagent (SendMessage) com as correções aplicadas; o relatório atribui cada rodada ao executor (linha `REVISORES:`).
- O revisor deve terminar com `ADVERSARIAL-VERIFICATION: SATISFEITO`, `CORRIGIR` ou `BLOQUEADO`, listando gaps por severidade.
- Se houver gap `REAL` de severidade `BLOQUEANTE` ou `ALTA`, corrigir sequencialmente e rodar nova verificação.
- Repetir até no máximo **3 rodadas** ou até o revisor declarar `SATISFEITO`.
- Não corrigir automaticamente item que dependa de decisão humana, D[n], credencial, ambiente externo ou mudança destrutiva; declarar como bloqueio/pendência.
- Usar status final `PENDENTE` quando o limite de 3 rodadas for atingido ou quando sobrarem apenas gaps `MEDIA`/`BAIXA` explicitamente aceitos como pendência.
- Ao final, reportar `ADVERSARIAL-LOOP: <n>/3 rodadas, status: <SATISFEITO|PENDENTE|BLOQUEADO>`.

**Argumentos de entrada do Council:**

Use bloco `ARGS:` no prompt. Custom agents Codex não recebem argumentos formais como função; os argumentos são contrato textual obrigatório.

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

- `START_AT=EXECUTION`: começa executando. Ainda faz leitura mínima de contexto/reuso e para apenas se encontrar decisão D[n] bloqueante.
- `START_AT=PLANNING`: começa criando/estruturando o plano. Roda **Planning Adversarial Loop** até 2 rodadas e escolhe automaticamente a melhor opção por trade-off quando `AUTO_DECIDE=true`.
- `START_AT=PLAN_REVIEW`: plano já existe. Ler `PLAN_SOURCE` ou bloco `PLAN:`, revisar o plano com **Planning Adversarial Loop** até 2 rodadas, executar se o review ficar `SATISFEITO`, e depois rodar o **Adversarial Verification Loop** da execução. Não refazer planejamento inicial amplo.
- `START_AT=AUTO`: inferir pelo verbo do usuário; “implemente/corrija/termine” = execução, “planeje/desenhe/audite estratégia” = planejamento, “plano já existe/revise execute” = plan review.
- `AUTO_DECIDE=true`: comparar trade-offs e escolher a melhor opção sem perguntar, exceto quando envolver ação destrutiva, credencial, prod/deploy, decisão de negócio irreversível ou ambiguidade D[n] realmente bloqueante.
- `PLAN_SOURCE` é obrigatório para `START_AT=PLAN_REVIEW` quando o plano não estiver colado no prompt; pode ser path, diff, issue ou indicação de bloco `PLAN:`.
- `AUTO_EXECUTE_AFTER_PLAN=false` é default em `START_AT=PLANNING`; em `START_AT=PLAN_REVIEW`, o default efetivo é `true`, porque esse modo significa “revisar plano existente, executar e revisar execução”. Use `AUTO_EXECUTE_AFTER_PLAN=false` apenas para review-only.
- `PLAN_REVIEW_MAX` não pode passar de 2; `EXECUTION_REVIEW_MAX` não pode passar de 3.

**Planning Adversarial Loop (quando `START_AT=PLANNING` ou `START_AT=PLAN_REVIEW`):**

- Máximo **2 rodadas**.
- O plano deve explicitar opções, delta de qualidade, delta de custo, breakeven, condição de não-adoção e decisão escolhida.
- Em `START_AT=PLAN_REVIEW`, revisar o plano existente como fonte de verdade inicial; se houver gap crítico corrigível, ajustar somente o plano necessário para torná-lo executável, sem voltar para discovery/planejamento amplo.
- Cada rodada é executada por SUBAGENT `learnhouse-adversarial-reviewer` (nunca inline pelo agente principal), mesma regra do Verification Loop; a rodada 2 pode continuar o mesmo subagent via SendMessage.
- O revisor deve terminar com `PLAN-ADVERSARIAL-VERIFICATION: SATISFEITO | REPLANEJAR | BLOQUEADO`.
- Se vier `REPLANEJAR` com gap crítico corrigível, revisar o plano e rodar a segunda rodada.
- Ao final, reportar `PLAN-ADVERSARIAL-LOOP: <n>/2 rodadas, status: <SATISFEITO|PENDENTE|BLOQUEADO>`.

## 0. LEI ZERO — NÃO REINVENTAR A RODA

Sou engenheiro integrador, não implementador. A maioria dos problemas já foi resolvida por times maiores, com mais usuários, mais bugs corrigidos. Reinventar é desperdício.

**Caso de referência:** 1 mês implementando kanban do zero, resultado subótimo. Depois descobri o `multica.ai` — mesma stack, ecossistema maduro, resolvia tudo e mais 20 coisas que eu jamais pensaria. Trabalho descartado por não ter buscado antes.

### Regra OBRIGATÓRIA

Antes de implementar qualquer feature não trivial:

1. UTILIZE O PLUGIN last30days@last30days-skill para buscar no GitHub, awesome-lists, Reddit, HackerNews repositórios open source maduros, validados, na nossa stack, que já resolvam o problema. Cada uma das features deve ser investigada individualmente. Vamos evitar ao máximo escrever código do zero. O principio é que tudo já foi feito em algum ecossistema maduro.
2. **Usar o plugin Context7** para auxiliar a busca e a leitura de documentação oficial dos candidatos encontrados.
3. Clonar, ler o código, entender as soluções já validadas.
4. Portar, copiar e reaproveitar tudo que for possível — libs, código, padrões, implementação.
5. Implementar do zero **apenas** se não houver absolutamente nada reaproveitável.

Default absoluto: portar e reaproveitar. Implementar do zero é exceção, não regra.

6) JAMAIS FAÇA MIGRAÇÕES EM BATCH: MIGRAÇÕES DEVEM SER SEMPRE SEQUENCIAIS. 1 POR VEZ E CONFERIDAS COM TESTES SE FORAM CORRETAMENTE IMPLEMENTADAS.

- APÓS ANALISAR INICIALMENTE:

0) É PROIBIDO PERGUNTAS DE CLARIFICAÇÃO SEM EXPLORAÇÃO APROFUNDADA DO CÓDIGO E DOS DADOS REAIS (DB dev local), POIS SÃO PERGUNTAS IDIOTAS SEMPRE E CAUSAM MAIS CONFUSÃO DO QUE ACERTO. VOCÊ TEM TODOS OS DADOS CONCRETOS NA MÃO PARA ACERTAR RESPOSTAS AO ANALISAR O CÓDIGO E DISTINCT VALUES NAS COLUNAS DAS TABELAS ALVOS. Só depois dessa análise profunda, se restar ambiguidade real, faça um bloco de decisão/pergunta para cada decisão aberta seguindo a seção 6: comportamento, exemplo aplicado bom, exemplo aplicado ruim e quando escolher. Depois monte o plano sequencial.

8) SEMPRE AO escrever código typescript, use o plugin typescript-lsp quando disponível na sessão

## 14. Consistência Antes de Alteração — DRY e Anti-Sobrecorreção

Aplica-se a qualquer mudança **transversal** (cross-cutting): safe-area/padding, responsividade, tokens de design, tratamento de estado, formatação, error handling — qualquer padrão que se repita em múltiplas telas/arquivos. NÃO se aplica a fix pontual de um único arquivo sem equivalente em outros lugares.

**Veredicto operacional:** antes de propor um padrão novo, provar qual padrão já existe. Inferir um tratamento "da cabeça" e aplicá-lo gera inconsistência e dívida de manutenção. Replica-se o que o código já adota — não o que parece razoável. Proibida a frase "o ideal seria [X]" sem antes provar, com path + linha, se [X] já é o padrão de fato.

### 14.1. Auditoria de Padrão Existente (Pré-Requisito Bloqueante)

Antes de qualquer plano, mapear o tratamento atual em TODO o código relevante:

1. **Varredura** — buscar (grep/serena) todas as ocorrências do problema E das soluções já existentes, pelo termo concreto do domínio (`safe-area-inset`, `pb-safe`, classe, hook, token, util).
2. **Evidência auditável** — para cada ocorrência: `path` + `Linha N` + qual tratamento está aplicado. Sem isso não há diagnóstico (Seção 8).
3. **Identificação do canônico** — havendo tratamento, qual é o padrão de fato? Havendo mais de um, qual vence? Declarar com dado: contagem de ocorrências, aderência ao framework de referência.

### 14.2. Clusterização e Escopo Determinístico

Não sair aplicando em tudo. Particionar o universo de telas/arquivos em 3 baldes, cada um com lista nominal de paths:

```
[A] Já tratado corretamente             → conforme ao canônico
[B] Não tratado                         → escopo de aplicação
[C] Tratado de forma divergente/parcial → escopo de normalização
```

Sem clusterização nominal e auditável (path + linha por item), não há execução. O plano resultante lista cada item de B e C com sua evidência e roda sequencialmente (Seção 11, LEI ZERO §6).

### 14.3. Centralização DRY (Default)

Repetir o mesmo bloco em N telas é o anti-padrão. O fix correto é **fonte única**:

- Extrair para componente wrapper, hook, util, classe utilitária, token ou layout compartilhado — o mecanismo que a stack oferecer.
- As telas consomem a fonte única. Mudança futura = 1 ponto de edição, propaga para todas.
- O mecanismo de centralização para problemas comuns (safe-area, responsividade, etc.) já é resolvido por frameworks de referência. Buscar e portar (Seção 0, Seção 9.2) — não inventar.
- Se a centralização NÃO for possível, justificar com dado (ex: variação legítima por tela que impede abstração).

### 14.4. Anti-Sobrecorreção

Estado final desejado: cada tela aplica o padrão **exatamente uma vez**. A estratégia define o tratamento do cluster A:

- **Patch-in-place (sem centralização):** A é intocável. Aplicar fix apenas em B ∪ C. Verificar idempotência — nunca empilhar segundo efeito onde já existe (ex: `padding-bottom` dobrado, dupla safe-area).
- **Centralização (14.3, default):** migra-se A, B e C para consumir a fonte única; o tratamento **local** em A é REMOVIDO ao adotar a fonte, senão soma. Migração 1-por-1 (LEI ZERO §6), com teste de regressão visual confirmando que a renderização de A não mudou.

### 14.5. Loop de Conhecimento (Anti-Frágil)

Padrão canônico descoberto/decidido na execução é incorporado ao doc de planejamento/wiki ao fim da tarefa:

1. Verificar se o caso já estava previsto no plano (ex: `PLANO_REFATORACAO_*.md`). Se sim, citar a seção.
2. Se não estava: documentar o padrão canônico, onde fica a fonte única e o critério de cluster — para que a próxima execução parta do norte e não refaça a auditoria do zero.
3. Cada iteração deixa o sistema mais robusto, não mais frágil.

## 15. Workflow Orchestration (adaptado de Boris Cherny)

Fonte: CLAUDE.md do Boris Cherny (gist.github.com/hqman/e29cb6386c539d795767e8c3fd2c959b) + howborisusesclaudecode.com. Cada princípio abaixo está MAPEADO no maquinário deste repo — usar a ferramenta local, não reinventar:

1. **Plan-first** — tarefa não-trivial (3+ passos ou decisão arquitetural) começa por plano (§6, council `START_AT=PLANNING`, skill `clarification-plan`). **Se algo der errado no meio da execução: PARE e replaneje imediatamente — não continue empurrando.** Plan mode também serve para VERIFICAÇÃO, não só para construir.
2. **Subagents liberais** — manter o contexto principal limpo: pesquisa, exploração e análise paralela vão para subagents (1 investigação por subagent; cap 6 via hook `subagent-throttle`). Problema difícil = jogar mais compute via subagents (council/adversarial loops), não insistir inline.
3. **Self-Improvement Loop** — §16 (executável, com hooks).
4. **Verification before done** — já ENFORCED por §10 (`prova-de-conclusao` + Stop hook `completion-gate` + `ui-evidence-gate`). Pergunta-guia do Boris adotada: **"um staff engineer aprovaria isto?"** — fazer a si mesmo ANTES de apresentar.
5. **Demand elegance (balanceado)** — para mudança não-trivial, antes de apresentar: "sabendo tudo que sei agora, existe solução mais elegante?". Fix que parece gambiarra = reimplementar do jeito certo. NÃO aplicar a fixes triviais (anti-over-engineering).
6. **Autonomous bug fixing** — bug report, teste falhando, CI vermelho: consertar direto (logs → causa raiz → fix → re-teste, §11), sem pedir hand-holding. Coerente com §0 (proibido pergunta sem exploração).

**Simplicidade primeiro (Boris, Core Principles):** toda mudança tão simples quanto possível; tocar o mínimo de código; nada de fix temporário — causa raiz sempre (padrão senior).

## 16. Self-Improvement Loop (lessons.md + hooks) — executável

Ciclo: **capturar → injetar → promover → consolidar**. O objetivo é a taxa de erro CAIR entre sessões.

- **Capturar (obrigação do agente):** após QUALQUER correção do Augusto (veredicto "Errado.", abordagem revertida, ponto cego apontado, review adversarial derrubando algo meu) → append IMEDIATO em `tasks/lessons.md` no formato `## [data] sintoma → regra` (2-4 linhas, padrão concreto, não desabafo). Não esperar o fim da sessão.
- **Injetar (hook, determinístico):** SessionStart roda `.claude/hooks/lessons-inject.sh` → as lições entram no contexto de TODA sessão nova. Reler antes de tarefa do mesmo domínio.
- **Promover (anti-recorrência):** lição que se repete 2× → vira (a) regra permanente na seção apropriada deste CLAUDE.md, ou (b) hook executável via plugin `hookify` (guard determinístico > instrução em prosa). Lição promovida é marcada `[PROMOVIDA → destino]` no lessons.md.
- **Consolidar (manutenção):** skill `claude-md-management:revise-claude-md` sob demanda; `/loop` sem argumentos roda o loop de manutenção de `.claude/loop.md` (lint da documentação do repo inteiro via `scripts/docs-wiki-lint.py`, ds-gate, lessons pendentes de promoção, árvore git suja).
- **Iterar impiedosamente** (Boris §3): se a mesma correção aparecer 3×, o problema é a REGRA mal escrita — reescrever a regra, não re-anotar o sintoma.

