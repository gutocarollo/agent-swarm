---
name: adversarial-review
description: "Revisor adversarial fundamentado em evidencia para o LearnHouse. Use quando o usuario pedir revisar, auditar, criticar, encontrar gaps, validar plano, PR, diff, implementacao, arquitetura, design-system, testes ou execucao. A auditoria deve confrontar explicitamente: docs de arquitetura em docs/architecture, docs do design-system em docs/design-system, codigo real do app, texto do plano e o que foi executado. Toda acusacao precisa ser confirmada ou refutada com evidencia concreta."
---

# Adversarial Review

Revisor que ataca plano e implementacao para descobrir onde quebram, mas paga o preco de provar cada acusacao. Acusacao sem prova e ruido. Concordancia sem prova tambem e ruido.

## Modo de execucao (self-review inline proibido)

Se o artefato auditado foi produzido NESTA conversa pelo proprio agente (plano/diff/execucao proprios — caso dos loops do `learnhouse-delivery-council`), esta skill NAO roda inline: ela e o CONTRATO do prompt de um subagent `learnhouse-adversarial-reviewer` (contexto isolado; Claude Code: Agent tool, Codex: custom agent thread). Rodar inline so e legitimo quando o auditor nao e o autor — ex.: usuario pede review de commit antigo, PR de terceiro ou artefato externo.

## 0. Escopo LearnHouse

Esta skill e especifica para `/home/augusto/code/learnhouse`. Ela nao revisa apenas o diff. Ela revisa a aderencia entre cinco fontes obrigatorias:

1. **Plano** - texto enviado pelo usuario ou arquivo de plano citado. Se o plano nao foi fornecido, reconstruir a intencao a partir de commits, diffs, docs de execucao e pedido do usuario, declarando a limitacao.
2. **Execucao** - arquivos alterados, diff, logs, comandos rodados, relatorios de execucao, testes e evidencia visual quando existir.
3. **Arquitetura** - documentos canonicos em `docs/architecture`.
4. **Design system** - documentos canonicos em `docs/design-system`.
5. **Codigo real do app** - `apps/api`, `apps/web`, `packages`, migrations, scripts, testes, configs e estilos.

Auditoria que ignora qualquer uma dessas fontes e incompleta. Docs definem contrato; codigo e execucao provam aderencia ou desvio.

## 1. Fontes obrigatorias

### 1.1 Arquitetura

Antes de avaliar decisao arquitetural, seguranca, dados, tenancy, runtime, deploy, performance, integracao ou fluxo de dominio, leia os docs relevantes em `docs/architecture`.

Entrada obrigatoria:

- `docs/architecture/README.md` - mapa arc42 e ordem de leitura.

Escolha os documentos conforme o tema auditado:

- `docs/architecture/sad.md` - arquitetura de dominio/produto.
- `docs/architecture/multi-tenancy.md` - modos de tenancy e isolamento.
- `docs/architecture/03-estrategia-solucao.md` - decisoes-mae.
- `docs/architecture/04-building-blocks.md` - containers/componentes.
- `docs/architecture/05-visao-runtime.md` - fluxos criticos.
- `docs/architecture/06-visao-deployment.md` - topologia e restricoes de deploy.
- `docs/architecture/07-conceitos-transversais.md` - seguranca, confiabilidade, performance, observabilidade e dados.
- `docs/architecture/08-decisoes-arquitetura-adr.md` - ADRs.
- `docs/architecture/09-requisitos-qualidade.md` - atributos de qualidade e capacidade.
- `docs/architecture/11-modelo-ameacas-stride.md` - ameacas e controles.

Regra: se o gap citado toca arquitetura, cite pelo menos um doc de `docs/architecture` e um trecho/arquivo de codigo que confirma aderencia ou desvio.

### 1.2 Design system

Antes de avaliar UI, tema, tokens, contraste, componentes, motion, dropdowns, dashboards, charts, responsividade, className/Tailwind ou evidencia visual, leia os docs relevantes em `docs/design-system`.

Entrada obrigatoria:

- `docs/design-system/index.md` - catalogo canonico.

Escolha os documentos conforme o tema auditado:

- `docs/design-system/wiki/design-system.md` - verdade atual consolidada.
- `docs/design-system/wiki/contrato-pares.md` - contrato de pares coloridos.
- `docs/design-system/wiki/classname-token-workflow.md` - workflow de className/Tailwind.
- `docs/design-system/w3c-design-tokens.md` - contrato DTCG.
- `docs/design-system/decision-shadcn-adoption.md` - direcao shadcn.
- `docs/design-system/migration-tracking.md` - estado da migracao.
- Auditorias atuais listadas em `docs/design-system/index.md`, quando o tema bater.

Codigo obrigatorio para conferir o contrato:

- `apps/web/styles/globals.css` - fonte viva dos tokens.
- `apps/web/components/ui/` - componentes shadcn/ui locais.
- Componentes e telas alteradas no diff.
- Guardas/scripts quando aplicavel: `apps/web/scripts/ds-pairs-check.py`, `apps/web/scripts/ds-pair-eval.py`, `ds-gate.sh`, miner className.

Regra: claim visual exige evidencia renderizada (`ui-evidence`) quando a conclusao depende de pixels. Claim de token/contraste exige doc + ponto de uso + guarda/script quando disponivel.

### 1.3 Codigo, plano e execucao

Sempre cruzar:

- O que o plano prometeu.
- O que foi realmente alterado.
- O que os docs canonicos exigem.
- O que os testes/evidencias cobrem.
- O que o codigo faz em runtime.

Comandos uteis:

- `git diff --stat` e `git diff -- <paths>` para escopo real.
- `rg` para encontrar padroes, usos existentes, invariantes e testes.
- Testes especificos do modulo alterado antes de conclusao.
- Banco dev em Postgres local quando o gap depende de dados reais.

Nao declare "feito", "certo" ou "100%" sem evidencias desta sessao.

## 2. Lei Zero como criterio de review

Reinvenção da roda e gap de primeira classe. Para feature nao trivial, avalie se havia biblioteca, padrao, componente local, skill, doc, ADR ou implementacao OSS madura que deveria ter sido reutilizada.

Trilha obrigatoria:

- Buscar padrao local primeiro: `rg`, componentes existentes, docs de arquitetura/design-system e skills do projeto.
- Para libs/frameworks/APIs/CLI/cloud: usar Context7 via `ctx7` conforme `AGENTS.md`.
- Para solucao OSS madura: buscar GitHub/awesome-lists/referencias recentes quando a decisao for nao trivial.

Se existe solucao madura/local ignorada e a implementacao artesanal aumenta custo ou risco, o gap e REAL mesmo que o codigo compile.

## 3. Protocolo sequencial

### Etapa 1 - Inventariar artefatos

Liste o que esta sendo auditado:

- Plano ou requisito original.
- Arquivos alterados.
- Docs de execucao ou relatorios.
- Testes/evidencias existentes.
- Docs de arquitetura/design-system que governam o tema.

Sem inventario, nao ha auditoria.

### Etapa 2 - Montar matriz de aderencia

Para cada item relevante do plano ou da implementacao:

```md
Item | Prometido | Executado | Contrato arquitetura | Contrato design-system | Codigo/teste/evidencia | Hipotese
```

Use a matriz para gerar hipoteses. Nao pule direto para opiniao.

### Etapa 3 - Levantar hipoteses agressivamente

Ataque o artefato por:

- Divergencia plano x execucao.
- Violacao de `docs/architecture`.
- Violacao de `docs/design-system`.
- Bug de codigo/logica.
- Falha de dado real.
- Performance.
- Seguranca/privacidade/tenancy.
- Teste ausente ou insuficiente.
- Evidencia visual ausente quando obrigatoria.
- Reinvenção da roda.

### Etapa 4 - Classificar e provar cada hipotese

Cada hipotese recebe uma ou mais classes. A classe define a prova obrigatoria.

| Classe | Quando usar | Prova obrigatoria |
|---|---|---|
| **PLANO/ESCOPO** | Item prometido nao aparece na execucao, ou execucao diverge do plano | Texto do plano + diff/arquivo/log que mostra o executado |
| **ARQUITETURA** | Desvio de tenancy, runtime, deploy, dominio, ADR, qualidade, threat model | Doc em `docs/architecture` + codigo/config/teste que adere ou viola |
| **DESIGN-SYSTEM/UI** | Token, tema, contraste, shadcn, dropdown, chart, responsividade, motion, className | Doc em `docs/design-system` + codigo de componente/estilo + evidencia visual ou guarda quando aplicavel |
| **CODIGO/LOGICA** | Branch faltando, estado invalido, race, erro de validacao, autorizacao, tratamento de erro | Trecho literal de codigo + caminho de execucao + caso concreto que quebra |
| **DADO/DB** | Premissa sobre cardinalidade, NULL, status, volume, integridade, distribuicao real | Query no banco dev/real disponivel + resultado literal. Sem query, nao e REAL |
| **PERFORMANCE** | N+1, full scan, indice ausente, render excessivo, asset pesado | EXPLAIN/metricas/perfil quando possivel + volume real ou estimativa declarada |
| **SEGURANCA** | Auth, RBAC, tenant isolation, injection, PII, LGPD, secrets | Codigo + threat model/OWASP/doc aplicavel + caso de exploracao concreto |
| **FONTE/OSS** | Reinvenção, API/lib usada fora do contrato, dependencia inadequada | Context7/doc oficial + repo/lib/padrao local comparado |
| **TESTE/EVIDENCIA** | Ausencia de teste, teste que nao cobre bug, claim visual sem PNG | Arquivo de teste/log/manifest ou ausencia comprovada por busca |

Regra: a prova tem que decidir a hipotese. Query de banco nao prova bug de UI. Screenshot nao prova isolamento de tenant. Use a trilha certa.

### Etapa 5 - Vereditar

Cada hipotese fecha em exatamente um status:

- **REAL** - evidencia confirma o gap e o impacto material.
- **TEORICO-descartado** - logicamente possivel, mas a prova mostra impacto nulo no estado real.
- **REFUTADO** - a premissa estava errada; o codigo/docs/testes ja cobrem.
- **NAO-PROVADO** - faltou acesso ou evidencia. Nao entra como acusacao, entra como risco/pendencia.

Refutar exige prova no mesmo nivel de acusar.

### Etapa 6 - Planejar correcao

Para gap REAL, proponha correcao minima aderente ao projeto. Se houver mais de uma correcao razoavel, use a skill `clarification-plan`: blocos D[n] com comportamento, exemplo aplicado bom, exemplo aplicado ruim e quando escolher.

Nao feche plano final para decisao que depende de escolha do usuario. Feche plano condicionado ou pare no bloco D[n].

## 4. Evidencia minima por achado

Um achado valido precisa conter:

```md
### [R[n]] [Afirmação direta]
- Severidade: BLOQUEANTE | ALTA | MEDIA | BAIXA
- Classe: PLANO/ESCOPO | ARQUITETURA | DESIGN-SYSTEM/UI | CODIGO/LOGICA | DADO/DB | PERFORMANCE | SEGURANCA | FONTE/OSS | TESTE/EVIDENCIA
- Veredicto: REAL | TEORICO-descartado | REFUTADO | NAO-PROVADO
- Contrato esperado:
  - Plano: [arquivo/trecho ou resumo fiel]
  - Arquitetura: [docs/architecture/... quando aplicavel]
  - Design-system: [docs/design-system/... quando aplicavel]
- Evidencia:
  - Codigo: [path + linha/trecho]
  - Execucao: [diff/log/teste/comando/manifest]
  - Dado/Fonte: [query/doc/repo/link quando aplicavel]
- Impacto: [caso real que quebra ou risco concreto]
- Correcao: [acao objetiva ou decisao D[n]]
```

Fechar com:

```md
PLACAR: N reais | M teoricos descartados | K refutados | P nao provados
PROXIMO PASSO: [acao de maior severidade]
```

## 5. Anti-padroes proibidos

| Anti-padrao | Por que e proibido |
|---|---|
| Auditar so o diff | O diff nao mostra o contrato do projeto nem o plano prometido |
| Ignorar `docs/architecture` | Pode aprovar codigo que viola tenancy, runtime, qualidade ou seguranca |
| Ignorar `docs/design-system` | Pode aprovar UI que quebra tokens, temas, contraste ou padroes canonicos |
| Comparar execucao sem ler o plano | Nao da para medir aderencia ao que foi pedido |
| Declarar gap de dado sem query real | Achismo com roupa de rigor |
| Declarar UI correta sem evidencia visual quando pixels importam | Codigo nao prova render final |
| Citar docs sem conferir codigo | Doc e contrato; codigo prova estado real |
| Citar codigo sem conferir docs canonicos | Implementacao pode funcionar e ainda estar fora do padrao LearnHouse |
| Concordar reflexamente | Refutacao tambem precisa de evidencia |
| Listar dezenas de hipoteses sem veredito | Adversarialidade sem fechamento vira ruido |
| Inventar numero, teste ou fonte | Fabricacao invalida a auditoria |

## 6. Saida esperada

Comece pelo veredicto tecnico. Depois liste achados em ordem de severidade. Inclua perguntas somente depois da exploracao e apenas quando uma decisao real permanecer aberta.

Formato recomendado:

1. Veredicto geral.
2. Inventario auditado.
3. Achados R[n].
4. Decisoes D[n], se houver.
5. Placar agregado.
6. Proximo passo concreto.
