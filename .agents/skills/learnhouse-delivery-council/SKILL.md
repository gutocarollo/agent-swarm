---
name: learnhouse-delivery-council
description: Use em tarefas complexas do LearnHouse que envolvam implementacao, planejamento, revisao de plano existente, arquitetura, design-system, banco, auth, tenancy, seguranca, testes, PR review ou qualquer mudanca que precise iniciar por EXECUTION, PLANNING, PLAN_REVIEW ou AUTO, com trade-off automatico e adversarial loops.
---

# LearnHouse Delivery Council

Coordene uma entrega dentro de `/home/augusto/code/learnhouse` usando Codex nativo: `AGENTS.md`, repo skills, custom agents, comandos reais e evidencia desta sessao.

## Argumentos de Entrada

Aceite argumentos em bloco `ARGS:`. Se o usuario nao enviar `ARGS`, inferir `START_AT=AUTO`.

```text
ARGS:
START_AT=EXECUTION | PLANNING | PLAN_REVIEW | AUTO
PLAN_SOURCE=<path | inline | issue | diff>
AUTO_DECIDE=true | false
PLAN_REVIEW_MAX=2
EXECUTION_REVIEW_MAX=3
AUTO_EXECUTE_AFTER_PLAN=false | true
```

Defaults:

- `START_AT=AUTO`
- `PLAN_SOURCE` omitido; use bloco `PLAN:` ou path citado no prompt quando existir.
- `AUTO_DECIDE=true`
- `PLAN_REVIEW_MAX=2`
- `EXECUTION_REVIEW_MAX=3`
- `AUTO_EXECUTE_AFTER_PLAN=false` para `START_AT=PLANNING`; default efetivo `true` para `START_AT=PLAN_REVIEW`

Limites:

- `PLAN_REVIEW_MAX` nunca pode passar de 2.
- `EXECUTION_REVIEW_MAX` nunca pode passar de 3.

Interprete:

- `START_AT=EXECUTION`: comece pela execucao. Faca apenas contexto minimo, reuso local e checagens bloqueantes antes de editar.
- `START_AT=PLANNING`: comece criando/estruturando o plano. Nao edite codigo ate concluir o Planning Adversarial Loop, a menos que `AUTO_EXECUTE_AFTER_PLAN=true`.
- `START_AT=PLAN_REVIEW`: plano ja existe. Leia `PLAN_SOURCE`, bloco `PLAN:` ou arquivo citado; revise o plano com Planning Adversarial Loop; se ficar `SATISFEITO`, execute; depois rode Adversarial Verification Loop da execucao. Nao refaca planejamento inicial amplo.
- `START_AT=AUTO`: inferir pelo pedido. "implemente", "corrija", "termine", "faça" e "aplique" indicam execucao; "planeje", "desenhe", "arquiteture", "avalie abordagem" indicam planejamento; "plano ja existe", "revise execute" e "review do plano aprovado" indicam plan review.
- `PLAN_SOURCE`: obrigatorio para `START_AT=PLAN_REVIEW` quando o plano nao estiver no prompt. Aceite path local, trecho colado, issue ou diff como fonte.
- `AUTO_EXECUTE_AFTER_PLAN`: se omitido, trate como `false` em `START_AT=PLANNING` e como `true` em `START_AT=PLAN_REVIEW`.

## Regra de Escopo

Use o fluxo completo quando a tarefa tiver risco medio/alto, tocar multiplos arquivos, alterar contrato de dominio, UI, dados, auth, tenancy, seguranca, arquitetura ou teste. Para um ajuste trivial de um arquivo, use uma versao compacta: contexto minimo, implementacao, validacao e relato.

Nao delegue ambiguidade crua ao usuario. Explore codigo, docs e dados reais primeiro. Se ainda houver decisao humana realmente bloqueante, use `$clarification-plan`.

## Fluxo Obrigatorio

1. Resolva o ponto de entrada (`START_AT`).
2. Produza um Context Brief proporcional ao ponto de entrada:
   - pedido real e objetivo verdadeiro;
   - docs relevantes lidos;
   - padroes locais encontrados com `rg`;
   - arquivos provaveis;
   - riscos e validacoes necessarias.
3. Procure reuso local antes de criar codigo novo:
   - componentes, hooks, services, scripts, ADRs, skills e docs existentes;
   - cite caminhos concretos quando um padrao governar a mudanca.
4. Resolva decisoes bloqueantes:
   - se `AUTO_DECIDE=true`, escolha automaticamente a melhor opcao por trade-off;
   - use `$clarification-plan` apenas para alternativa que ainda precise de decisao humana real;
   - nao implemente escolhas D[n] ainda abertas quando envolverem decisao humana real.
5. Se `START_AT=PLANNING` ou `START_AT=PLAN_REVIEW`, execute o Planning Adversarial Loop.
6. Se `START_AT=PLANNING` e `AUTO_EXECUTE_AFTER_PLAN=false`, pare apos o Planning Adversarial Loop com plano revisado/aprovado.
7. Se `START_AT=PLAN_REVIEW`, execute somente depois de `PLAN-ADVERSARIAL-VERIFICATION: SATISFEITO`, salvo `AUTO_EXECUTE_AFTER_PLAN=false`, que transforma o modo em review-only.
8. Se seguir para execucao, implemente de forma sequencial:
   - altere o menor conjunto de arquivos que satisfaz o plano;
   - preserve mudancas locais nao relacionadas;
   - nao adicione dependencias de producao sem justificativa explicita.
9. Valide com comandos reais:
   - rode testes, typecheck, lint, queries, scripts ou evidencia visual conforme o risco;
   - claim visual exige evidencia renderizada quando pixels importam;
   - claim de dado exige query ou prova equivalente.
10. Execute o Adversarial Verification Loop para execucao.
11. Relate sem inflar conclusao:
   - diga exatamente o que mudou;
   - liste comandos rodados e resultados;
   - declare gaps ou riscos restantes.

## Trade-off Automatico No Planejamento

Quando `AUTO_DECIDE=true`, escolha automaticamente a melhor opcao usando:

- delta de qualidade;
- delta de custo;
- breakeven;
- condicao de nao-adocao;
- reversibilidade;
- aderencia a docs e padroes locais.

So peca decisao humana quando a melhor opcao depender de:

- acao destrutiva;
- credencial, pagamento ou acesso externo;
- prod/deploy;
- decisao de negocio irreversivel;
- ambiguidade D[n] que nao possa ser resolvida por codigo, docs ou dados reais.

## Planning Adversarial Loop

Execute quando `START_AT=PLANNING` ou `START_AT=PLAN_REVIEW`.

Limite: maximo de 2 rodadas.

### Rodada de planejamento

1. Produza ou revise o plano com opcoes e trade-offs.
   - Em `START_AT=PLANNING`, produza/estruture o plano.
   - Em `START_AT=PLAN_REVIEW`, trate o plano existente como fonte inicial; ajuste apenas gaps criticos corrigiveis, sem refazer discovery/planejamento amplo.
2. Rode `$adversarial-review` ou use `learnhouse-adversarial-reviewer` contra o plano, docs e codigo real relevante.
3. Exija encerramento:

```md
PLAN-ADVERSARIAL-VERIFICATION: SATISFEITO | REPLANEJAR | BLOQUEADO
GAPS-CRITICOS: N
DECISAO-ESCOLHIDA: [opcao escolhida ou bloqueio]
PROXIMA-ACAO: [executar | replanejar | pedir decisao]
```

Se o review retornar `REPLANEJAR` com gap critico corrigivel, revise o plano e rode a segunda rodada. Pare em `SATISFEITO`, `BLOQUEADO` ou 2 rodadas.

Regra de gate: execucao so pode iniciar a partir de planejamento quando a ultima rodada de review do plano retornar `PLAN-ADVERSARIAL-VERIFICATION: SATISFEITO`. Se a segunda rodada retornar `REPLANEJAR`, o status final do planning loop e `PENDENTE` e a execucao NAO pode comecar, mesmo que o agente incorpore o gap logo depois. Incorporar gap apos review conta como novo replanejamento; sem nova rodada adversarial satisfatoria, o plano continua nao aprovado.

Em `START_AT=PLANNING`, depois de `SATISFEITO`:

- se `AUTO_EXECUTE_AFTER_PLAN=true`, avance para execucao;
- se `AUTO_EXECUTE_AFTER_PLAN` estiver omitido ou `false`, pare com o plano revisado/aprovado.

Em `START_AT=PLAN_REVIEW`, depois de `SATISFEITO`:

- se `AUTO_EXECUTE_AFTER_PLAN` estiver omitido ou `true`, avance para execucao;
- se `AUTO_EXECUTE_AFTER_PLAN=false`, pare com o plano revisado e reporte review-only.

Em `REPLANEJAR` na rodada final:

- reporte `PLAN-ADVERSARIAL-LOOP: 2/2, status: PENDENTE`;
- nao execute;
- nao escreva "pendente formalmente" se a execucao continuou, porque isso mascara um gate quebrado;
- peca nova rodada/novo chamado apos o plano corrigido, ou pare com a pendencia declarada.

Ao final, reporte:

```md
PLAN-ADVERSARIAL-LOOP: <rodadas>/2, status: <SATISFEITO|PENDENTE|BLOQUEADO>
```

## Adversarial Verification Loop

Execute este loop ao final de tarefa de risco medio/alto.

Limite: maximo de 3 rodadas.

### Rodada

1. Rode `$adversarial-review` ou use `learnhouse-adversarial-reviewer`.
2. Exija que o review compare:
   - pedido/plano original;
   - diff e arquivos alterados;
   - docs de arquitetura quando aplicavel;
   - docs do design-system quando aplicavel;
   - codigo real;
   - comandos e evidencias desta sessao.
3. Exija que o review termine com:

```md
ADVERSARIAL-VERIFICATION: SATISFEITO | CORRIGIR | BLOQUEADO
GAPS-CRITICOS: N
PROXIMA-ACAO: [corrigir | parar | pedir decisao]
```

### Criterio de correcao

Corrija sequencialmente e rode nova rodada quando houver gap `REAL` com severidade `BLOQUEANTE` ou `ALTA`.

Nao corrija automaticamente:

- decisao D[n] sem escolha do usuario;
- acao destrutiva;
- credencial, pagamento ou acesso externo;
- deploy/prod sem procedimento especifico;
- gap `NAO-PROVADO` que precise de evidencia indisponivel.

### Criterio de parada

Pare quando:

- o review retornar `ADVERSARIAL-VERIFICATION: SATISFEITO`;
- completar 3 rodadas;
- sobrar apenas gap `MEDIA`/`BAIXA` aceito explicitamente como pendencia;
- sobrar bloqueio real fora do alcance da sessao.

Na resposta final, inclua:

```md
ADVERSARIAL-LOOP: <rodadas>/3, status: <SATISFEITO|PENDENTE|BLOQUEADO>
```

## Fontes Obrigatorias

Sempre comece por:

- `AGENTS.md`
- plano, issue, diff ou prompt fornecido pelo usuario
- codigo real sob `apps/api`, `apps/web`, `packages`, migrations, scripts e testes

Leia tambem quando o tema exigir:

- Arquitetura: `docs/architecture/README.md` e documentos relevantes em `docs/architecture`
- UI/design-system: `docs/design-system/index.md`, docs relevantes em `docs/design-system`, `apps/web/styles/globals.css` e `apps/web/components/ui`
- Banco/dados: schema, migrations, services e queries no banco dev quando a conclusao depender de cardinalidade, status, NULL, integridade ou distribuicao real
- Ferramentas, SDKs, frameworks, APIs, CLI ou cloud: documentacao atual conforme `AGENTS.md`

## Saida Minima

Para tarefas completas, entregue nesta ordem:

1. Veredicto tecnico ou estado da entrega.
2. Context Brief.
3. Plano sequencial ou decisoes D[n].
4. Arquivos alterados.
5. Comandos de validacao com resultado.
6. Resultado do Adversarial Verification Loop ou justificativa de por que nao se aplicava.
7. Pendencias reais.

## Uso Com Subagents

Subagents sao opcionais e devem ser pedidos explicitamente pelo usuario ou usados quando a tarefa for paralelizavel. Preferir:

- `learnhouse-context-scout` para exploracao read-only;
- `learnhouse-implementer` para execucao apos decisoes resolvidas;
- `learnhouse-adversarial-reviewer` para auditoria read-only;
- `learnhouse-test-auditor` para validar se a evidencia sustenta o claim.

Sempre espere todos terminarem antes de consolidar achados. Nao use subagents para fugir de uma decisao que exige leitura direta de instrucoes da skill pelo agente principal.
