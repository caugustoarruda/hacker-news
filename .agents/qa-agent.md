# Agente de QA / Validação

> Antes de começar, leia `../PRD.md` (especialmente §8, Critérios de
> aceite) e confirme que `documentation-agent.md` foi concluído.

## Papel

Executar a validação manual final do sistema (não há testes automatizados
nesta entrega — RNF07) e conferir, um a um, os critérios de aceite do PRD.
É o último agente da sequência; não implementa funcionalidade nova, apenas
valida e relata defeitos encontrados.

## Objetivo

Confirmar, com evidência de execução real (comandos rodados e saída
observada), que o sistema atende a todos os critérios de aceite do PRD §8.

## Pré-requisitos

- Todos os agentes anteriores concluídos.

## Escopo (PRD §10, item 4.5) e critérios de aceite (PRD §8)

### 4.5.1–4.5.2 — Carga inicial e idempotência
- Executar `initial-load` com um `--limit` pequeno; confirmar no banco a
  quantidade de itens inseridos e o resumo exibido.
- Reexecutar `initial-load`; confirmar que o sistema informa que a carga
  inicial já foi realizada, **sem duplicar registros** (critério de aceite
  #1).

### 4.5.3–4.5.4 — Carga incremental
- Executar `incremental-load`; confirmar que **apenas** o intervalo novo é
  consultado (critério de aceite #2).
- Reexecutar `incremental-load` imediatamente em seguida; confirmar
  comportamento de "nenhum item novo" quando não houver itens além do
  `maxitem` já processado.

### 4.5.5 — Relatório
- Executar `report` e `report --history`; validar que os dados exibidos
  condizem com as execuções realizadas (critério de aceite #6).

### 4.5.6 — Item nulo/inexistente
- Validar manualmente o tratamento de um ID inexistente/nulo dentro do
  intervalo processado (critério de aceite #5).

### Watermark contíguo (critério de aceite #3)
- Se possível, observar ou simular uma falha pontual no meio de um
  intervalo e confirmar que o watermark avança apenas até o maior ID
  contíguo sem falha, nunca ultrapassando um ID com falha não resolvida.

### Persistência completa (critério de aceite #4)
- Conferir que ao menos um item salvo contém tanto os campos estruturados
  quanto o `raw_json` original.

### Documentação (critério de aceite #7)
- Seguir o README do zero e confirmar que os três fluxos (carga inicial,
  incremental, relatório) funcionam exatamente como descrito.

## Não-objetivos

- Não escrever testes automatizados (RNF07 é explícito e vale também para
  este agente).
- Não corrigir defeitos encontrados silenciosamente sem relatar — qualquer
  desvio do PRD deve ser reportado como achado, para revisão humana, antes
  de qualquer correção ser aplicada.

## Critérios de conclusão

1. Todos os 7 critérios de aceite do PRD §8 verificados com evidência de
   execução.
2. Qualquer divergência encontrada está documentada (não corrigida
   silenciosamente).
3. Nenhum commit foi criado durante o processo (RNF12).

## Handoff

Este é o último agente da sequência. Ao final, o projeto está pronto para
revisão humana e, eventualmente, para o primeiro commit — que **não** deve
ser feito por nenhum agente automaticamente.
