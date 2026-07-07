# lessons.md — self-improvement loop (CLAUDE.md §16)

> Formato: `## [YYYY-MM-DD] sintoma → regra`. Capturar IMEDIATAMENTE após correção do Augusto,
> review adversarial que derrubou algo, ou ponto cego descoberto. 2-4 linhas, padrão concreto.
> Lição repetida 2× → promover a regra do CLAUDE.md ou hook (hookify) e marcar `[PROMOVIDA → destino]`.
> Injetado em toda sessão nova via `.claude/hooks/lessons-inject.sh` (SessionStart).

## [2026-07-07] Anexar/ler artefato gigante estourou o contexto → dado grande nunca entra inteiro
Anexar o JSON de mineração (~10MB/~3M tokens) matou a sessão instantaneamente ("prompt too long").
**Regra:** artefato >1MB nunca via @menção/Read. Shape via `jq`/`head` (streaming), consulta via SQL
(Postgres `classname_mining`) ou subagent. Se um workflow produz JSON gigante, o fix é materializar
em tabelas consultáveis, não ler com mais cuidado.

## [2026-07-07] Criei estrutura de skill sem provar o padrão do repo → duplicação divergente
Coloquei scripts/doc em `.claude/skills/` sem checar que `.agents/skills/` era a cópia canônica
versionada e que skill do repo = só SKILL.md (scripts em `apps/web/scripts/`). Resultado: 2 cópias
divergindo 23 linhas, detectado só em varredura posterior.
**Regra:** antes de criar/mover arquivo de convenção, provar o padrão com `git ls-files` + `ls` nas
instâncias existentes (§14.1). Pedido literal do usuário não dispensa a auditoria de padrão — divergência
consciente se declara na hora, não se descobre depois.

## [2026-07-07] Inventei detalhe ao portar lógica (distinct no roleSignature) → 110 arestas corrompidas
Ao portar o fingerprint do miner p/ SQL, escrevi "sorted distinct roles" — o miner (L968) NÃO deduplica.
O planning adversarial pegou; sem ele, `edge_cluster_entity` nasceria silenciosamente errada.
**Regra:** portar lógica = citar arquivo:linha da fonte para CADA transformação e replicar literalmente
(collation, duplicatas, ordem). Review adversarial ANTES de ingestão/migração, não depois.

## [2026-07-07] Entreguei sem fechar o loop de conhecimento → wiki desatualizada cobrada depois
Camada relacional entregue sem atualizar wiki Karpathy/log/index (§14.5 e SKILL §7 exigem).
**Regra:** entrega que muda verdade de design-system/processo só fecha com log.md + página wiki +
`design-system-wiki-lint.py` verde no MESMO turno da entrega.

## [2026-07-07] Declarei "curado e indexado" com lint que só via .md×index → órfãos e canon podre passaram
Após a curadoria, `assets/` (2.5MB, 17 arquivos) tinha 0 referências vivas, uma auditoria RESOLVIDA
seguia listada como ativa, e um canon (galeria de temas) estava com pixels pré-07-06 sem aviso.
O lint verde me deu falsa confiança: ele não cobria não-markdown, nem frescor.
**Regra:** "curado" = checklist por TIPO de artefato (md, json, dir de prints, canon-frescor), não
lint-verde. Guard novo só conta depois de teste NEGATIVO (simular o órfão e ver o FAIL) — o primeiro
guard que escrevi tinha furo (ancestral genérico "sources" cobria qualquer coisa) e só o teste pegou.
[PROMOVIDA → scripts/docs-wiki-lint.py (repo-wide) cobre não-md; frescor de canon segue manual no /loop]

## [2026-07-07] Tratei wiki Karpathy como design-system → escopo real era repo inteiro
A curadoria nasceu em `docs/design-system`, mas `docs/index.md`/`docs/log.md` já eram do repo inteiro.
Manter skill, loop e lint com nome/escopo design-system fazia o agente limpar só uma categoria e seguir
tomando decisão errada em planos, auditorias, arquitetura e commercial.
**Regra:** toda tarefa de "wiki", "Karpathy", naming, doc órfão ou doc legado usa `repo-wiki-curator`,
`docs/SCHEMA.md` e `python3 scripts/docs-wiki-lint.py`; design-system é apenas um `--scope`.
[PROMOVIDA → .claude/CLAUDE.md bloco "Repo Wiki / Documentação = Karpathy temporal"]

## [2026-07-07] sed cego para "corrigir ref" corrompeu linha que já estava certa
Ao corrigir refs quebradas, apliquei `sed 's#old#new#'` em globals.css — mas a linha JÁ tinha o path
correto; o tool flaggava por substring do nome antigo dentro do path válido. O sed duplicou o prefixo
(`.../sources/docs/design-system/sources/...`).
**Regra:** antes de sed/edit para "corrigir ref", confirmar que a linha NÃO resolve já (o achado pode ser
falso-positivo-substring do próprio detector). Preferir o resolve-guard no detector a editar o arquivo.
Edit exato (com contexto lido), nunca sed cego, para correção de ref.

## [2026-07-07] Report do council omitiu QUEM executou as reviews → usuário concluiu que subagents não rodaram
As 4 rodadas adversariais RODARAM em subagent (Agent transcript linhas 1408/1931 + SendMessage 1431/1999),
mas os labels ("Planning Adversarial Loop 2/2") não atribuíam executor, e a skill dizia "subagents são
opcionais" — comportamento certo por escolha, não por contrato. O contexto estourou pela implementação
inline (130 Bash + 76 Edit + 25 Write), não pelas reviews (54KB de 7,1MB = 0,75%).
**Regra:** review adversarial SEMPRE em subagent; todo bloco de loop reporta linha `REVISORES:` com o
executor de cada rodada; fase mecânica em lote vai para `learnhouse-implementer`.
[PROMOVIDA → learnhouse-delivery-council SKILL.md (2 espelhos) + CLAUDE.md bloco council + adversarial-review]
