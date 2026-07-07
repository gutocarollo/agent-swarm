---
name: clarification-plan
description: Use quando uma tarefa, auditoria, plano de correção, decisão técnica ou clarificação tiver mais de uma opção possível e o usuário precisar escolher com base em consequências concretas. Obriga blocos D[n] com comportamento, exemplo aplicado bom, exemplo aplicado ruim, quando escolher, e terceira via quando A/B forem insuficientes.
---

# Clarification Plan

Use esta skill sempre que houver mais de uma opção possível para resolver, planejar, corrigir, auditar ou clarificar qualquer coisa.

## Regra central

É proibido fazer pergunta seca como "quer A ou B?", "qual você prefere?" ou listar opções sem consequências práticas.

Antes de pedir escolha do usuário, explique o comportamento concreto de cada opção e mostre exemplos reais aplicados ao contexto. O objetivo é nortear a escolha, não transferir ambiguidade crua para o usuário.

## Formato obrigatório

Para cada decisão aberta, crie um bloco:

```md
### D[n] — R[x]/[item relacionado]: [pergunta concreta da decisão]

**Opção A — [nome da opção]**

- **Comportamento:** se escolhermos esta opção, o sistema/processo fará [efeito concreto].
- **Exemplo aplicado bom:** no caso real [entidade/tabela/arquivo/comando/lead/job], acontecerá [resultado bom].
- **Exemplo aplicado ruim:** no caso real [entidade/tabela/arquivo/comando/lead/job], acontecerá [risco/falha/custo].
- **Quando escolher:** escolha esta opção se a prioridade for [critério].

**Opção B — [nome da opção]**

- **Comportamento:** ...
- **Exemplo aplicado bom:** ...
- **Exemplo aplicado ruim:** ...
- **Quando escolher:** ...
```

Não há limite artificial de decisões. Em auditorias longas, se houver D1-D12, escreva D1-D12.

## Terceira via obrigatória

Se nenhuma opção individual for boa, proponha uma **Opção C**, combinação, spike, fallback ou estratégia híbrida. Explique por que A e B isoladas são insuficientes.

Exemplo de terceira via válida:

```md
**Opção C — spike mínimo + fallback obrigatório**

- **Comportamento:** manter o resolver atual, criar fixtures reais, testar a alternativa e só adotar se provar ganho.
- **Exemplo aplicado bom:** se a lib nova corrigir nomes que o resolver manual não cobre, ela entra como camada auxiliar.
- **Exemplo aplicado ruim:** se a lib não gerar o nome recorrompido necessário para buscar no filesystem, ela não substitui o caminho manual.
- **Quando escolher:** quando A e B isoladas têm risco alto e a união/fallback pode cobrir mais casos.
```

## Exemplo aplicado

Um exemplo aplicado deve citar uma entidade, fluxo, tabela, coluna, comando, arquivo, lead, mensagem, endpoint, job, dado, tela ou cenário real do contexto analisado. Não use analogias genéricas.

Formato mínimo:

```md
Se escolhermos [opção], então no caso real [cenário concreto], o sistema fará [comportamento]. Isso é bom porque [ganho]. Isso é ruim/perigoso quando [caso de falha].
```

## Auditorias e planos

Quando a tarefa envolver auditoria com itens R1, R2, R3 etc., cada item deve separar:

- Veredito: concordo, discordo ou parcialmente.
- Prova: 100% provado, parcialmente provado ou não provado.
- Evidências concretas.
- Plano de correção.
- Decisões pendentes no formato D[n].

Pode haver plano preliminar por item, mas não feche implementação final de item que depende de escolha do usuário. Monte plano condicionado por opção ou pare no bloco de clarificação.
